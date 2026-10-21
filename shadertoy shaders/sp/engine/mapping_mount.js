(()=>{
 const M=window.HeartMapping,H=window.HeartHardwareMapping;if(!M||!H)return;
 const panel=M.mount;for(const child of panel.children)child.hidden=true;
 const extended=document.createElement('div');panel.append(extended);
 const midi=document.createElement('div');midi.className='hardware-mapping-panel';midi.hidden=true;M.addTab('intech','Intech',midi);
 H.mount(midi,extended);window.heartHardwareMappingMounted=true;
 const oldHardware=window.heartHardwareState;window.heartHardwareState=info=>{oldHardware?.(info);H.hardware(info);};
 const oldFrame=window.heartControllerFrame;window.heartControllerFrame=f=>H.frame(f)||oldFrame?.(f)||false;
 window.heartMappingTab=id=>{midi.hidden=id!=='intech';};window.heartMappingsPaint=H.paint;
})();
