"""Offline mocks only: never binds ports, starts services, or sends commands."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('proposed_launch',HERE.parents[1]/'launch.py')
launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch)
ROOT=HERE.parents[1]

class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.root=patch.object(launch,'ROOT',ROOT);self.root.start();self.addCleanup(self.root.stop)
        self.http=patch.object(launch.urllib.request,'build_opener');self.opener=self.http.start().return_value;self.addCleanup(self.http.stop)
        self.response=self.opener.open.return_value.__enter__.return_value
        self.response.status=200
        self.response.geturl.return_value='http://127.0.0.1:8765/status.html'
        self.response.read.return_value=(ROOT/'engine/status.html').read_bytes()
        self.socket=patch.object(launch,'connect');self.connect=self.socket.start();self.addCleanup(self.socket.stop)
        self.ws=self.connect.return_value.__enter__.return_value
        self.state={'arena_connected':False,'hold':True,'clips':[],'layers':[],'fx':[], 'patch_operation':{},'delivery':{}}
        self.ws.recv.return_value=json.dumps(self.state)

    def test_expected_service_accepts_held_arena_disconnected_state(self):
        self.assertTrue(launch.heart_ready());self.ws.send.assert_not_called()
        self.connect.assert_called_once_with('ws://127.0.0.1:8766/',open_timeout=1,close_timeout=.2,max_size=4*1024*1024,proxy=None)

    def test_unrelated_http_rejected_without_websocket(self):
        self.response.read.return_value=b'<title>Another app</title>'
        self.assertFalse(launch.heart_ready());self.connect.assert_not_called()

    def test_redirect_rejected(self):
        self.response.geturl.return_value='http://example.invalid/'
        self.assertFalse(launch.heart_ready());self.connect.assert_not_called()

    def test_http_error_rejected(self):
        self.response.status=404;self.assertFalse(launch.heart_ready())

    def test_http_timeout_rejected(self):
        self.opener.open.side_effect=TimeoutError;self.assertFalse(launch.heart_ready())

    def test_unrelated_websocket_rejected(self):
        for msg in ['{}','[]','not json',json.dumps({'arena_connected':True})]:
            with self.subTest(msg=msg):
                self.ws.recv.return_value=msg;self.assertFalse(launch.heart_ready())

    def test_wrong_types_rejected(self):
        for k,v in [('hold',1),('arena_connected','yes'),('clips',{}),('delivery',[])]:
            with self.subTest(key=k):
                self.ws.recv.return_value=json.dumps({**self.state,k:v});self.assertFalse(launch.heart_ready())

    def test_non_websocket_port_rejected(self):
        self.connect.side_effect=OSError;self.assertFalse(launch.heart_ready())

    def test_silent_websocket_rejected(self):
        self.ws.recv.side_effect=TimeoutError;self.assertFalse(launch.heart_ready())

class LaunchFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=HERE);self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);(self.root/'engine').mkdir()
        binary=self.root/'monitor/Heart.app/Contents/MacOS/Heart';binary.parent.mkdir(parents=True);binary.touch()
        for name,value in [('ROOT',self.root),('listening',MagicMock(return_value=True)),('start',MagicMock()),('heart_ready',MagicMock(return_value=True))]:
            p=patch.object(launch,name,value);p.start();self.addCleanup(p.stop)
        p=patch.object(launch.subprocess,'run');self.run=p.start();self.addCleanup(p.stop)
        p=patch.object(launch,'wait_for',side_effect=lambda check,*args:check());p.start();self.addCleanup(p.stop)

    def test_existing_expected_service_only_opens_monitor(self):
        launch.main();launch.start.assert_not_called();self.run.assert_called_once_with(['/usr/bin/open',str(self.root/'monitor/Heart.app')],check=True)

    def test_existing_unrelated_service_never_launches_or_builds(self):
        launch.heart_ready.return_value=False
        with self.assertRaisesRegex(RuntimeError,'session was left intact'):launch.main()
        launch.start.assert_not_called();self.run.assert_not_called()

    def test_one_port_occupied_preserves_protective_error(self):
        launch.listening.side_effect=lambda port:port==8765
        with self.assertRaisesRegex(RuntimeError,'still starting'):launch.main()
        launch.start.assert_not_called();self.run.assert_not_called()

    def test_cold_start_retains_engine_arguments_and_checks_identity(self):
        launch.listening.side_effect=lambda port:port==8770
        with patch.object(launch,'arena_ready',return_value=True), patch.object(launch,'wait_for',side_effect=lambda check,*a:check() if check==launch.heart_ready else True):
            launch.main()
        launch.start.assert_called_once_with(['heart.py','--all'],self.root/'engine',self.root/'engine/heart.log')
        launch.heart_ready.assert_called_once()

if __name__=='__main__':unittest.main()
