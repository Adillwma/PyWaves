# -*- coding: utf-8 -*-

# PyWaves v1.0.0
# Build created on Friday July 28th 2023
# Author: Adill Al-Ashgar
# University of Bristol
# @Adill: adillwmaa@gmail.co.uk 

### To-do list ###
# [Done]Add a save animation button
# [Done]Update the save animation button to show to user that it is saving not frozen
# [Done]Add a pause button
# [Done]Add a play button
# [Done]Add a refrence button that will capture the current shown wave and display it in red behind the animation as a still image
# [Done]Add button to hide or clear the refrence wave (maybe both?) (maybe turn the capture button into a toggle button?)
# Add a reset button that resets all settings and clears the screena and all line data 
# Make it so that updating frequency or amplitude doesn't affect the entire wave plotted so far, just the wave as drawn from then on
# Sort out the y axis scale slider and the labels for both of those sliders
# Look into beating due to mismatch between time base and animation frame rate? decouple these if not already? or possibly mathc them ?
# Add other waveforms? square, triangle, sawtooth, etc
# Allow user to input the values for sliders by keyboard input for precision and ease of use
# Decide wether to continue to save the enitre figure as the animation or perhaps to just save the waveform windown only?

#%% - Program Settings 
# Animation
wave_fidelity = 1000   # Number of points to plot in the sine wave
fps = 30               # Frames per second of the animation (time between frames is 1/fps)

# Initial frequency and amplitude values
initial_frequency = 1.0      # Frequency in Hz
initial_amplitude = 1.0      # Amplitude (normalised unitless)

# Initial plot window
initial_time_length = 4
initial_amplitude_scale = 2.1


#%% - Dependencies
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
from matplotlib.widgets import Slider, Button, TextBox

#%% - Internal Program Initialization

# Aditional Parameters
reference_occupied = False
show_sum_enabled = False
ref_frequency = initial_frequency
ref_amplitude = 0
ref_time_index = 0


### Functions ###
def init():
    line.set_data([], [])
    return line,

def update_time_length(val):
    new_time_length = time_length_slider.val
    ax.set_xlim(0, new_time_length)
    fig.canvas.draw_idle()

def update_amp_scale_length(val):
    amplitude_scale = amplitude_scale_slider.val
    ax.set_ylim(-amplitude_scale, amplitude_scale)
    fig.canvas.draw_idle()

def animate(i):
    global ref_i
    ref_i = i 

    # Wave
    x = np.linspace(0, time_length_slider.val, wave_fidelity)
    y = amplitude_slider.val * np.sin(2 * np.pi * frequency_slider.val * (x - 0.01 * i))
    line.set_data(x, y)

    # Reference
    if reference_occupied:
        yref = ref_amplitude * np.sin(2 * np.pi * ref_frequency * (x - 0.01 * ref_time_index))
        ref_plot.set_data(x, yref)

    # Sum
    if show_sum_enabled:
        calculate_sum()

    return line, ref_plot, line_sum

def play_animation(event):
    freeze_plot.set_data([], [])
    ref_freeze_plot.set_data([], [])
    sum_freeze_plot.set_data([], [])
    anim.event_source.start()

def pause_animation(event):
    frozen_wave = line.get_data()
    frozen_ref = ref_plot.get_data()
    frozen_sum = line_sum.get_data()
    anim.event_source.stop()
    freeze_plot.set_data(frozen_wave[0], frozen_wave[1])
    ref_freeze_plot.set_data(frozen_ref[0], frozen_ref[1])
    sum_freeze_plot.set_data(frozen_sum[0], frozen_sum[1])

def capture_reference(event):
    global reference_occupied
    global show_sum_enabled
    global ref_frequency, ref_amplitude, ref_time_index
    if reference_occupied: # clears the reference if it was occupied
        ref_plot.set_data([], [])
        reference_occupied = False
        if show_sum_enabled: # resets the show sum button if it was enabled
            show_sum_enabled = False
            line_sum.set_data([], [])
            button_show_sum.label.set_text('Show\nSum')
        # Change the text of the button
        button_cap_ref.label.set_text('Capture\nReference')
        fig.canvas.draw_idle()
    else:   
        # Capture the current plot and display it in red behind the animation as a still image
        reference_occupied = True
        # Change the text of the button
        button_cap_ref.label.set_text('Clear\nReference')
        #redraw button
        fig.canvas.draw_idle()
        ref_frequency = frequency_slider.val
        ref_amplitude = amplitude_slider.val
        ref_time_index = ref_i

def show_sum_toggle(event):
    if reference_occupied:
        global show_sum_enabled
        # Check if the button is enabled or disabled and display a label accordingly
        if show_sum_enabled:
            show_sum_enabled = False
            line_sum.set_data([], [])
            button_show_sum.label.set_text('Show\nSum')
            fig.canvas.draw_idle()
        else:
            show_sum_enabled = True
            button_show_sum.label.set_text('Hide\nSum')
            fig.canvas.draw_idle()

def calculate_sum():
    if reference_occupied:
        live_wave = line.get_data()[1]
        ref_wave = ref_plot.get_data()[1]
        sum_wave = live_wave + ref_wave
        line_sum.set_data(line.get_data()[0], sum_wave)

def save_animation(event):
    button_save.label.set_text('Saving...\nAnimation')
    plt.pause(0.1)
    writergif = PillowWriter(fps=fps)
    anim.save('sine_wave3.gif', writer=writergif)
    button_save.label.set_text('Save\nAnimation')

def update_fr_from_text(text):
    # Update the slider value from the text input
    try:
        frequency_slider.set_val(float(text))
    except ValueError:
        pass

def update_am_from_text(text):
    # Update the slider value from the text input
    try:
        amplitude_slider.set_val(float(text))
    except ValueError:
        pass

### Compute ###
plt.style.use('seaborn-pastel')

fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(bottom=0.3)  # Adjust the bottom margin to make space for sliders

# Create time_length slider
ax_time_length = plt.axes([0.125, 0.2, 0.775, 0.012], facecolor='lightgoldenrodyellow')
time_length_slider = Slider(ax=ax_time_length, label='Time Scale', valmin=0.0001, valmax=60.0, valinit=initial_time_length)  #valfmt=None to hide the numerical readout
time_length_slider.valtext.set_visible(False)

# Create amplitude scaling slider (horizontal)
ax_amplitude_scale = plt.axes([0.91, 0.296, 0.007, 0.584], facecolor='lightgoldenrodyellow')
amplitude_scale_slider = Slider(ax=ax_amplitude_scale, label='Amplitude Scale', valmin=0.1, valmax=5.0,
                                valinit=initial_amplitude_scale, orientation='vertical')
amplitude_scale_slider.valtext.set_visible(False)

# Create frequency slider
ax_frequency = plt.axes([0.2, 0.02, 0.65, 0.03], facecolor='lightgoldenrodyellow')
frequency_slider = Slider(ax=ax_frequency, label='Frequency', valmin=1.0, valmax=20.0, valinit=initial_frequency, color='blue')
"""   # ADD BACK IN WHEN FIXED
frequency_slider.valtext.set_visible(False)
# Create a text input box to replace value readout with one that user can also type into for exact values
fr_text_box_ax = plt.axes([0.89, 0.02, 0.01, 0.03])
fr_text_box = TextBox(fr_text_box_ax, '', initial=str(frequency_slider.val) + " Hz")
fr_text_box.on_submit(update_fr_from_text)
"""

# Create amplitude slider
ax_amplitude = plt.axes([0.2, 0.06, 0.65, 0.03], facecolor='lightgoldenrodyellow')
amplitude_slider = Slider(ax=ax_amplitude, label='Amplitude', valmin=0., valmax=1.0, valinit=initial_amplitude, color='blue')
"""   # ADD BACK IN WHEN FIXED
amplitude_slider.valtext.set_visible(False)
# Create a text input box to replace value readout with one that user can also type into for exact values
am_text_box_ax = plt.axes([0.89, 0.06, 0.01, 0.03])
am_text_box = TextBox(am_text_box_ax, '', initial=str(amplitude_slider.val))
am_text_box.on_submit(update_am_from_text)
"""

# Create buttons
ax_play = plt.axes([0.20, 0.85, 0.1, 0.05])
ax_pause = plt.axes([0.325, 0.85, 0.1, 0.05])
ax_cap_ref = plt.axes([0.45, 0.85, 0.1, 0.05])
ax_show_sum = plt.axes([0.575, 0.85, 0.1, 0.05])
ax_save = plt.axes([0.7, 0.85, 0.1, 0.05])

button_play = Button(ax_play, 'Play', color='lightblue', hovercolor='0.975')
button_pause = Button(ax_pause, 'Pause', color='lightblue', hovercolor='0.975')
button_cap_ref = Button(ax_cap_ref, 'Capture\nReference', color='lightblue', hovercolor='0.975')
button_show_sum = Button(ax_show_sum, 'Show\nSum', color='lightblue', hovercolor='0.975')
button_save = Button(ax=ax_save, label='Save\nAnimation', color='lightblue', hovercolor='0.975')

# Connect button and slider actions
button_play.on_clicked(play_animation)
button_pause.on_clicked(pause_animation)
button_save.on_clicked(save_animation)
button_cap_ref.on_clicked(capture_reference)
button_show_sum.on_clicked(show_sum_toggle)
time_length_slider.on_changed(update_time_length)
amplitude_scale_slider.on_changed(update_amp_scale_length)

# Initialize lines
line, = ax.plot([], [], c='blue', lw=3)
freeze_plot, = ax.plot([], [], color='blue', lw=3)

ref_plot, = ax.plot([], [], color='red', lw=2, label='Ref')
ref_freeze_plot, = ax.plot([], [], color='red', lw=2)

line_sum, = ax.plot([], [], color='green', lw=1, alpha=0.7, label='Sum')
sum_freeze_plot, = ax.plot([], [], color='green', alpha=0.7, lw=1)

# Setup plot
ax.set_xlabel('Time (s)')
ax.set_ylabel('Amplitude')
title_y_position = 1.05  # Adjust this value to move the title up or down
ax.set_title('Sine Wave Visualizer', y=title_y_position)
ax.set_xlim(0, initial_time_length)
ax.set_ylim(-initial_amplitude_scale, initial_amplitude_scale)
ax.legend(loc='upper right')
ax.grid(alpha=0.3)
# Add the title above the bottom two sliders
plt.figtext(0.5, 0.10, 'Waveform Settings', ha='center', fontsize=10, color='black')

# Run Animation and show or save it
anim = FuncAnimation(fig, animate, init_func=init, frames=None, interval=1/fps*1000, blit=True)   #interval *1000 to convert seconds to ms
plt.show()
