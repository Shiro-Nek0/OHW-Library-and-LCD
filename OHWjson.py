import json
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

show_gpu_mem = None
gpu_fan_rpm = None

def space_pad(number, length):
    """
    Return a number as a string, padded with spaces to make it the given length

    :param number: the number to pad with spaces (can be int or float)
    :param length: the specified length
    :returns: the number padded with spaces as a string
    """

    number_length = len(str(number))
    spaces_to_add = length - number_length
    return (' ' * spaces_to_add) + str(number)

def get_local_json_contents(json_filename):
    """
    Returns the contents of a (local) JSON file

    :param json_filename: the filename (as a string) of the local JSON file
    :returns: the data of the JSON file
    """

    try:
        with open(json_filename) as json_file:
            try:
                data = json.load(json_file)
            except ValueError:
                print('Contents of "' + json_filename + '" are not valid JSON')
                raise
    except IOError:
        print('An error occurred while reading "' + json_filename + '"')
        raise

    return data

def get_json_contents(json_url):
    """
    Return the contents of a (remote) JSON file

    :param json_url: the url (as a string) of the remote JSON file
    :returns: the data of the JSON file
    """

    data = None

    req = Request(json_url)
    try:
        response = urlopen(req, timeout = 2).read()
    except HTTPError as e:
        print('HTTPError ' + str(e.code))
    except URLError as e:
        print('URLError ' + str(e.reason))
    else:
        try:
            data = json.loads(response.decode('utf-8'))
        except ValueError:
            print('Invalid JSON contents')

    return data

def find_in_data(ohw_data, name):
    """
    Search in the OpenHardwareMonitor data for a specific node, recursively

    :param ohw_data:    OpenHardwareMonitor data object
    :param name:        Name of node to search for
    :returns:           The found node, or -1 if no node was found
    """
    if ohw_data == -1:
        raise Exception('Couldn\'t find value ' + name + '!')
    if ohw_data['Text'] == name:
        # The node we are looking for is this one
        return ohw_data
    elif len(ohw_data['Children']) > 0:
        # Look at the node's children
        for child in ohw_data['Children']:
            if child['Text'] == name:
                # This child is the one we're looking for
                return child
            else:
                # Look at this children's children
                result = find_in_data(child, name)
                if result != -1:
                    # Node with specified name was found
                    return result
    # When this point is reached, nothing was found in any children
    return -1

def get_temperature_number(temp_str):
    """
    Given a temperature string of the form "48.8 °C", return the first number
    (in this example, 48). Also handles strings of the form "48,8 Â°C" that
    apparently can exist (at least when reading the response from a file)
    :param temp_str:    Temperature string
    :return:    Temperature number (in string form)
    """
    if 'Â' in temp_str:
        return temp_str[:-6]
    else:
        return temp_str[:-5]

def get_hardware_info(ohw_ip, ohw_port, cpu_name,ram_name, gpu_name, gpu_mem_size):
    """
    Get hardware info from OpenHardwareMonitor's web server and format it
    """
    global show_gpu_mem
    global gpu_fan_rpm

    # Init arrays
    my_info = {}
    gpu_info = {}
    ram_info = {}
    cpu_info = {}

    cpu_core_temps = []
    cpu_core_clocks = []
    
    # Get actual OHW data
    ohw_json_url = 'http://' + ohw_ip + ':' + ohw_port + '/data.json'
    data_json = get_json_contents(ohw_json_url)

    # Get info for CPU
    cpu_data = find_in_data(data_json, cpu_name)

    cpu_temps = find_in_data(cpu_data, 'Temperatures')
    cpu_clocks = find_in_data(cpu_data, 'Clocks')
    cpu_package_temp = find_in_data(cpu_temps, 'CPU Package')
    cpu_load = find_in_data(cpu_data, 'CPU Total')

    # Look for CPU temperatures. For all children of the CPU temp. section...
    for core_temp in cpu_temps['Children']:
        # Check that "Core" is in the name, to prevent using Intel's
        # "CPU Package" temperature, and should work with AMD too.
        if 'Core' in core_temp['Text']:
            # Remove '.0 °C' from end of value
            cpu_core_temps.append(get_temperature_number(core_temp['Value']))

    # Look for CPU clocks. For all children of the CPU clock.

    for core_clock in cpu_clocks['Children']:
        if 'Core' in core_clock['Text']:
            cpu_core_clocks.append((core_clock['Value'][:-4]))

    cpu_info['name'] = cpu_name
    cpu_info['load'] = cpu_load['Value'][:-4]
    cpu_info['temp'] = cpu_package_temp['Value'][:-5]
    cpu_info['temps'] = cpu_core_temps
    cpu_info['clocks'] = cpu_core_clocks
    my_info['cpu'] = cpu_info

    # Get info for RAM
    
    ram_data = find_in_data(data_json, ram_name)
    ram_load = find_in_data(ram_data, 'Load')
    ram_memory_load = find_in_data(ram_load, 'Memory')
    ram_info['name'] = ram_name
    ram_info['load'] = ram_memory_load['Value'][:-4]

    ram_mem_data = find_in_data(ram_data, 'Data')
    ram_used = find_in_data(ram_mem_data, 'Used Memory')
    ram_available = find_in_data(ram_mem_data, 'Available Memory')

    ram_info['used'] = ram_used['Value'].replace(' ', '')
    ram_info['available'] = ram_available['Value'].replace(' ', '')
    ram_info['total'] = "{}{}".format(round(float(ram_info['used'][:-2])+float(ram_info['available'][:-2])),ram_info['available'][-2:])
    my_info['ram'] = ram_info

    # Get info for GPU
    gpu_data = find_in_data(data_json, gpu_name)
    gpu_info['name'] = gpu_name
    gpu_clocks = find_in_data(gpu_data, 'Clocks')
    gpu_load = find_in_data(gpu_data, 'Load')

    gpu_core_clock = find_in_data(gpu_clocks, 'GPU Core')
    gpu_mem_clock = find_in_data(gpu_clocks, 'GPU Memory')
    gpu_temp = find_in_data(find_in_data(gpu_data, 'Temperatures'), 'GPU Core')
    gpu_core_load = find_in_data(gpu_load, 'GPU Core')
    fan_percent = find_in_data(find_in_data(gpu_data, 'Controls'), 'GPU Fan')

    # Check if the GPU has fan RPM info or just PWM info (percentage)
    if gpu_fan_rpm is None:
        gpu_fans = find_in_data(gpu_data, 'Fans')
        gpu_fan_rpm = (gpu_fans != -1)

    # Get data for GPU fans (or PWM percentage)
    if gpu_fan_rpm:
        gpu_fans = find_in_data(gpu_data, 'Fans')
    else:
        gpu_fans = find_in_data(gpu_data, 'Controls')

    # Get GPU Fan RPM info (check both Fans > GPU and Fans > GPU Fan)
    fan_rpm = find_in_data(gpu_fans, 'GPU')
    if fan_rpm == -1:
        fan_rpm = find_in_data(gpu_fans, 'GPU Fan')

    # Check if the GPU has used memory information, and remember it
    if show_gpu_mem is None:
        gpu_mem_percent = find_in_data(gpu_load, 'GPU Memory')
        show_gpu_mem = (gpu_mem_percent != -1)

    # Get GPU Memory percentage if it exists, otherwise GPU voltage
    if show_gpu_mem:
        # Get GPU memory percentage
        gpu_mem_percent = find_in_data(gpu_load, 'GPU Memory')

        # Calculate used MBs of GPU memory based on the percentage
        used_percentage = float(
            gpu_mem_percent['Value'][:-2].replace(",", "."))
        used_mb = int((gpu_mem_size * used_percentage) / 100)

        # Add to GPU info object
        gpu_info['used_mem'] = used_mb
        gpu_info['free_memory'] = round(float(find_in_data(gpu_data, 'GPU Memory Free')['Value'][:-3]))
    else:
        # Get GPU voltage
        voltages = find_in_data(gpu_data, 'Voltages')
        core_voltage = find_in_data(voltages, 'GPU Core')
        gpu_info['voltage'] = core_voltage['Value'][:-2]

    # Add rest of GPU info to GPU object
    gpu_info['temp'] = get_temperature_number(gpu_temp['Value'])
    gpu_info['load'] = gpu_core_load['Value'][:-4]
    gpu_info['core_clock'] = gpu_core_clock['Value'][:-4]
    gpu_info['mem_clock'] = gpu_mem_clock['Value'][:-4]
    gpu_info['fan_percent'] = fan_percent['Value'][:-4]
    gpu_info['fan_rpm'] = fan_rpm['Value'][:-4]

    # Add GPU info to my_info
    my_info['gpu'] = gpu_info

    return my_info