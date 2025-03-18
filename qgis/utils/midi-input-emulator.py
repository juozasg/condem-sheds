import mido
import os

input_ports = mido.get_input_names() # type: ignore


input = mido.open_input("KeyLab mkII 61:KeyLab mkII 61 MIDI 36:0")
for message in input:
    if(message.type == 'note_off'):
        char = chr(900 + message.note)
        # print('---')
        print(char)
        # exec command line
        os.system(f'input-emulator kbd type {char}')
        # print('+++')







# print("Available MIDI Input Ports:")
# if input_ports:
#     for i, port in enumerate(input_ports):
#         print(f"  {i}: {port}")