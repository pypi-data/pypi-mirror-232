#!/usr/bin/env python3
from ttkbootstrap import LabelFrame, OptionMenu, Button, Entry, Label, Checkbutton # type: ignore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gui import GUI # type: ignore
from ..gui_windows.advanced_compression_window import AdvancedCompressionWindow # type: ignore
from .right_clicker import RightClicker # type: ignore
from ..__init__ import __version__ # type: ignore

class CompFrame:
    def __init__(self, gui: "GUI"):
        self.gui = gui
        self.frame = LabelFrame(self.gui.scrollable_frame, borderwidth=1, text='Compression options')
        self.frame.grid_columnconfigure(2, weight = 1)

        self.no_compress_help_btn = Button(self.frame, text='?', width=1, command=lambda: self.gui.cb_msg_block(self.gui.help['comp']['no_compress']), bootstyle='secondary')
        self.no_compress_lbl = Label(self.frame, text='No compression')
        self.no_compress_cbox = Checkbutton(self.frame, variable=self.gui.no_compress_var, command=self.cb_nocompress, onvalue=True, offvalue=False, bootstyle='danger-round-toggle')

        self.comp_preset_help_btn = Button(self.frame, text='?', width=1, command=lambda: self.gui.cb_msg_block(self.gui.help['comp']['preset']), bootstyle='secondary')
        self.comp_preset_lbl = Label(self.frame, text='Preset')
        self.comp_preset_opt = OptionMenu(self.frame, self.gui.comp_preset_var, self.gui.comp_preset_var.get(), *self.gui.compression_presets.keys(), command=self.cb_comp_apply_preset, bootstyle='secondary')
        self.comp_preset_opt.config(width=15)

        self.steps_help_btn = Button(self.frame, text='?', width=1, command=lambda: self.gui.cb_msg_block(self.gui.help['comp']['steps']), bootstyle='secondary')
        self.steps_lbl = Label(self.frame, text='Number of steps')       
        self.steps_entry = Entry(self.frame, textvariable=self.gui.steps_var, width=8)
        self.steps_entry.bind('<Button-3><ButtonRelease-3>', RightClicker)

        self.processes_help_btn = Button(self.frame, text='?', width=1, command=lambda: self.gui.cb_msg_block(self.gui.help['comp']['processes']), bootstyle='secondary')
        self.processes_lbl = Label(self.frame, text='Number of processes')
        self.processes_entry = Entry(self.frame, textvariable=self.gui.processes_var, width=8)
        self.processes_entry.bind('<Button-3><ButtonRelease-3>', RightClicker)

        self.comp_advanced_btn = Button(self.frame, text='Advanced...', command=self.cb_compress_advanced, bootstyle='secondary')

        self.no_compress_help_btn.grid(column=0, row=0, sticky='w', padx=3, pady=3)
        self.no_compress_lbl.grid(column=1, row=0, sticky='w', padx=3, pady=3)
        self.no_compress_cbox.grid(column=2, row=0, sticky='nes', padx=3, pady=3)

        self.comp_preset_help_btn.grid(column=0, row=1, sticky='w', padx=3, pady=3)
        self.comp_preset_lbl.grid(column=1, row=1, sticky='w', padx=3, pady=3)
        self.comp_preset_opt.grid(column=2, row=1, sticky='nes', padx=3, pady=3)

        self.steps_help_btn.grid(column=0, row=2, sticky='w', padx=3, pady=3)
        self.steps_lbl.grid(column=1, row=2, sticky='w', padx=3, pady=3)
        self.steps_entry.grid(column=2, row=2, sticky='nes', padx=3, pady=3)

        self.processes_help_btn.grid(column=0, row=3, sticky='w', padx=3, pady=3)
        self.processes_lbl.grid(column=1, row=3, sticky='w', padx=3, pady=3)
        self.processes_entry.grid(column=2, row=3, sticky='nes', padx=3, pady=3)

        self.comp_advanced_btn.grid(column=2, row=4, sticky='nes', padx=3, pady=3)

        self.cb_comp_apply_preset()
        self.cb_nocompress()
    
    def cb_comp_apply_preset(self, *args):
        selection = self.gui.comp_preset_var.get()
        if selection == 'auto':
            output_option = self.gui.get_output_name()
            if output_option == 'local':
                self.gui.no_compress_var.set(True)
            elif output_option == 'imessage':
                selection = 'imessage_small'
                self.gui.no_compress_var.set(False)
            else:
                selection = output_option
                self.gui.no_compress_var.set(False)
            self.cb_nocompress()

        self.gui.fps_min_var.set(self.gui.compression_presets[selection]['fps']['min'])
        self.gui.fps_max_var.set(self.gui.compression_presets[selection]['fps']['max'])
        self.gui.res_w_min_var.set(self.gui.compression_presets[selection]['res']['w']['min'])
        self.gui.res_w_max_var.set(self.gui.compression_presets[selection]['res']['w']['max'])
        self.gui.res_h_min_var.set(self.gui.compression_presets[selection]['res']['h']['min'])
        self.gui.res_h_max_var.set(self.gui.compression_presets[selection]['res']['h']['max'])
        self.gui.quality_min_var.set(self.gui.compression_presets[selection]['quality']['min'])
        self.gui.quality_max_var.set(self.gui.compression_presets[selection]['quality']['max'])
        self.gui.color_min_var.set(self.gui.compression_presets[selection]['color']['min'])
        self.gui.color_max_var.set(self.gui.compression_presets[selection]['color']['max'])
        self.gui.duration_min_var.set(self.gui.compression_presets[selection]['duration']['min'])
        self.gui.duration_max_var.set(self.gui.compression_presets[selection]['duration']['max'])
        self.gui.img_size_max_var.set(self.gui.compression_presets[selection]['size_max']['img'])
        self.gui.vid_size_max_var.set(self.gui.compression_presets[selection]['size_max']['vid'])
        self.gui.img_format_var.set(self.gui.compression_presets[selection]['format']['img'])
        self.gui.vid_format_var.set(self.gui.compression_presets[selection]['format']['vid'])
        self.gui.fake_vid_var.set(self.gui.compression_presets[selection]['fake_vid'])
        self.gui.default_emoji_var.set(self.gui.compression_presets[selection]['default_emoji'])
        self.gui.steps_var.set(self.gui.compression_presets[selection]['steps'])

        self.gui.highlight_fields()
    
    def cb_compress_advanced(self, *args):
        AdvancedCompressionWindow(self.gui)
    
    def cb_nocompress(self, *args):
        if self.gui.no_compress_var.get() == True:
            state = 'disabled'
        else:
            state = 'normal'
        
        self.comp_advanced_btn.config(state=state)
        self.steps_entry.config(state=state)
        self.processes_entry.config(state=state)
    
    def set_inputs_comp(self, state: str):
        self.comp_preset_opt.config(state=state)
        self.comp_advanced_btn.config(state=state)
        self.steps_entry.config(state=state)
        self.processes_entry.config(state=state)
            
    def set_states(self, state: str):
        self.no_compress_cbox.config(state=state)
        self.set_inputs_comp(state=state)
