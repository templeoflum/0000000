import tkinter as tk
from tkinter import messagebox

class FiveStepModuleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Five-Step Module")
        self.root.geometry("600x400")

        # Steps list
        self.steps = ["Plan", "Draft", "Reflect", "Refine", "Finalize"]
        self.current_step_index = 0

        # A seed variable for your synergy logic, defaulted to 0.5
        self.seed_value = tk.DoubleVar(value=0.5)

        # Main container for the step frames
        self.step_frame = tk.Frame(self.root)
        self.step_frame.pack(fill=tk.BOTH, expand=True)

        # Navigation frame (Next, Back, etc.)
        nav_frame = tk.Frame(self.root)
        nav_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Buttons for navigation
        self.back_button = tk.Button(nav_frame, text="Back", command=self.prev_step, width=10)
        self.back_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.next_button = tk.Button(nav_frame, text="Next", command=self.next_step, width=10)
        self.next_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.finish_button = tk.Button(nav_frame, text="Finish", command=self.finish, width=10)
        self.finish_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Create frames for each step
        self.step_frames = []
        for step in self.steps:
            frame = tk.Frame(self.step_frame)
            self.step_frames.append(frame)
            # Each frame gets a label just to identify it
            tk.Label(frame, text=f"Step: {step}", font=("Arial", 14, "bold")).pack(pady=10)

            # Optionally add a scrolled text for user notes, or minimal label, etc.
            tk.Label(frame, text=f"This is the {step} step.\n\n"
                                 f"TODO: Insert synergy logic or placeholders here.\n\n"
                                 f"Seed = {self.seed_value.get()} (Will update if changed)",
                     justify=tk.LEFT).pack()

        # Create a seed slider at the bottom for synergy
        self.create_seed_slider()

        # Show the first step
        self.show_current_step()

        # Update button states
        self.update_nav_buttons()

    def create_seed_slider(self):
        """ Creates a horizontal slider for controlling 'seed_value'. """
        slider_frame = tk.Frame(self.root)
        slider_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(slider_frame, text="Adjust Seed Value:").pack(side=tk.LEFT, padx=5)
        seed_slider = tk.Scale(slider_frame, from_=0, to=1, resolution=0.01,
                               orient=tk.HORIZONTAL, length=300,
                               variable=self.seed_value,
                               command=self.on_seed_changed)
        seed_slider.pack(side=tk.LEFT, padx=5)

    def on_seed_changed(self, val):
        """
        Called whenever the seed slider is moved.
        We can update some synergy logic or text if needed.
        """
        # For demonstration, we just print the new seed and update the label in the current step
        print(f"DEBUG: Seed changed to {self.seed_value.get():.2f}")
        self.refresh_step_label()

    def refresh_step_label(self):
        """
        Refresh label text in the current step to reflect new seed value.
        """
        # Minimal approach: find the label in the current frame with the text we want to replace
        # For demonstration, we assume the label is child #2 in self.step_frames
        current_frame = self.step_frames[self.current_step_index]
        # A naive approach: we know there's a second label in each frame
        # that has "TODO: Insert synergy logic..." text. We'll just re-pack it
        for widget in current_frame.winfo_children():
            if isinstance(widget, tk.Label) and "TODO" in widget.cget("text"):
                new_text = (f"This is the {self.steps[self.current_step_index]} step.\n\n"
                            f"TODO: Insert synergy logic or placeholders here.\n\n"
                            f"Seed = {self.seed_value.get():.2f} (Will update if changed)")
                widget.config(text=new_text)
                break

    def show_current_step(self):
        """ Hides all step frames except the current one. """
        for i, frame in enumerate(self.step_frames):
            frame.pack_forget()
        self.step_frames[self.current_step_index].pack(fill=tk.BOTH, expand=True)

    def update_nav_buttons(self):
        # If current_step_index is 0, disable Back
        if self.current_step_index <= 0:
            self.back_button.config(state=tk.DISABLED)
        else:
            self.back_button.config(state=tk.NORMAL)

        # If current_step_index is last, disable Next
        if self.current_step_index >= len(self.steps) - 1:
            self.next_button.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)

    def next_step(self):
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.show_current_step()
            self.update_nav_buttons()

    def prev_step(self):
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.show_current_step()
            self.update_nav_buttons()

    def finish(self):
        """
        Called when 'Finish' is pressed, e.g. Final step is done.
        Could run synergy or store final data.
        """
        messagebox.showinfo("Finish", "You have completed the 5-step process!")
        # TODO: Integrate synergy or final data saving here if needed.

def main():
    root = tk.Tk()
    app = FiveStepModuleApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
