import json
import re
import os
from pathlib import Path
import datetime as dt
#--------------------------------------------------------------------------------------------------
# Get channels names from stream 
#--------------------------------------------------------------------------------------------------
def get_channels(line):
    # /01 0300 00 /02 0217 00 /03 0222 00 /04 0803 00 /05 0311 00 /06 0204 00
    channel_ids = ['/01', '/02', '/03', '/04', '/05', '/06']
    channels = ['NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL']
    ch_nbr = -1
    ch_count = 0
    json_data=open('Drive Parameters/kdm90_channels.json', 'r')
    ch_json = json.load(json_data)
    for ch in channel_ids:
        ch_nbr += 1
        ch_i = line.find(ch)
        if (ch_i != -1):
            for item in ch_json:
                if (item['id'] == str(line[ch_i+4:ch_i+8])):
                    ch_name = item['description'] + ' [' + item['scaling']+ ']'
                    channels[ch_nbr] = ch_name
            ch_count += 1
    print(len(channels))
    return channels, ch_count #return channels and their description + amount of channels used


#---------------------------------------------------------------------------------------------------------
# Cleans unwanted strings from drive's DSP's debug port stream file and saves the cleaned stream to a file 
#---------------------------------------------------------------------------------------------------------
def clean_terminal_data_stream(input_file, output_file):
    print('Cleaning debug port stream ("' + input_file + ' => ' + output_file + '")')         
    with open(input_file, 'r') as f:
        c = open(output_file, 'w')
        line_nbr = 0
        discarded = 0
        stripped = 0
        ok_lines = 0
        channels_got = False
        ch_count = 0
        for line in f:
            line_nbr +=1
            alkiot = line.split()

            # search for unknown targets 
            if (re.match(r'# KDL32', line)):
                print('ERROR!!! KDL32 channel definitions not available => errors in channel names and scaling possible!')

            # search for update interval 
            if (re.match(r'# KDMCPU', line)):
                dt = int(alkiot[3].strip("ms"))*0.001

            # search for channel definitions
            # /01 0300 00 /02 0217 00 /03 0222 00 /04 0803 00 /05 0311 00 /06 0204 00
            if (re.match(r'# /', line)):
                if (channels_got == False):
                    print('  Channel definitions found at line ' + str(line_nbr) + ' , decoding channel names...')
                    channels, ch_count = get_channels(line)
                    print(ch_count)
                    channels_got = True

            if (re.match(r'^#.*', line)):
                discarded += 1
            if not line.strip():
                discarded += 1
            elif (len(alkiot) < ch_count):
                discarded += 1
            else:
                if re.match(r'^Out_Floor', line):
                    stripped += 1
                    line = re.sub('^Out_Floor', '', line)
                elif re.match(r'^to_Floor type, side, code: [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{5}.[0-9]{4}', line):
                    stripped += 1
                    line = re.sub('^to_Floor type, side, code: [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{5}.[0-9]{4}', '', line)
                elif re.match(r'^to_Floor ', line):
                    stripped += 1
                    line = re.sub('^to_Floor ', '', line)
                elif re.match(r'^type, side, code: [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{5}.[0-9]{4}', line):
                    stripped += 1
                    line = re.sub('^type, side, code: [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{3} [0-9]{5}.[0-9]{4}', '', line)
                elif re.match(r'^\n', line):
                    stripped += 1
                    line = re.sub('^\n', '', line)
                elif (len(alkiot) != ch_count):
                    print('ERROR! New pattern (' + line + ') detected at line ' + str(line_nbr) + '!')
                    pass
                else:
                    ok_lines += 1
                if (len(alkiot) == ch_count):
                    c.write(line.replace(" ", ",", ch_count-1))   # write the stripped line    

        c.close()
        print('  Cleaned ' +  str(discarded+stripped+ok_lines) + ' lines (' + str(discarded) + ' discarded, ' + str(stripped) + ' stripped, '  + str(ok_lines) + ' ok)')
        print('  dt = ' + str(dt) + ' s')
        
        for i in range(len(channels)):
            print('  Channels[' + str(i) + '] = ' + channels[i])
        
    return dt, channels   # data interval [s], channel names and scalings

