# import argparse
# import threading
# import traceback
# import msgpackrpc
# from pathlib import Path
# import glob
# import time
# import os
# import json
# import sys
# import subprocess
# import errno
# import signal
# import copy


# AIRSIM_SETTINGS_TEMPLATE = {
#   "SeeDocsAt": "https://microsoft.github.io/AirSim/settings/",
#   "SettingsVersion": 1.2,
#   "SimMode": "Multirotor",
#   "ClockSpeed": 10,
#   "ViewMode": "NoDisplay",
#   "PhysiceEngineName": "ExternalPhysicsEngine",
#   "Recording": {
#     "RecordInterval": 1,
#     "Enabled": False,
#     "Cameras": []
#   },
#   "Vehicles": {
#     "Drone_1": {
#       "VehicleType": "SimpleFlight",
#       "UseSerial": False,
#       "LockStep": True,
#       "AutoCreate": True,
#       "X": 0,
#       "Y": 0,
#       "Z": 0,
#       "Roll": 0,
#       "Pitch": 0,
#       "Yaw": 0,
#       "Cameras": {
#         "FrontCamera": {
#           "X": 1,
#           "Y": 0,
#           "Z": 0,
#           "Pitch": 0,
#           "Roll": 0,
#           "Yaw": 0,
#           "CaptureSettings": [
#             {
#               "ImageType": 0,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             },
#             {
#               "ImageType": 2,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             }
#           ]
#         },
#         "RearCamera": {
#           "X": -1,
#           "Y": 0,
#           "Z": 0,
#           "Pitch": 0,
#           "Roll": 0,
#           "Yaw": 180,
#           "CaptureSettings": [
#             {
#               "ImageType": 0,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             },
#             {
#               "ImageType": 2,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             }
#           ]
#         },
#         "LeftCamera": {
#           "X": 0,
#           "Y": -1,
#           "Z": 0,
#           "Pitch": 0,
#           "Roll": 0,
#           "Yaw": -90,
#           "CaptureSettings": [
#             {
#               "ImageType": 0,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             },
#             {
#               "ImageType": 2,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             }
#           ]
#         },
#         "RightCamera": {
#           "X": 0,
#           "Y": 1,
#           "Z": 0,
#           "Pitch": 0,
#           "Roll": 0,
#           "Yaw": 90,
#           "CaptureSettings": [
#             {
#               "ImageType": 0,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             },
#             {
#               "ImageType": 2,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             }
#           ]
#         },
#         "DownCamera": {
#           "X": 0,
#           "Y": 0,
#           "Z": 0,
#           "Pitch": -90,
#           "Roll": 0,
#           "Yaw": 0,
#           "CaptureSettings": [
#             {
#               "ImageType": 0,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             },
#             {
#               "ImageType": 2,
#               "Width": 256,
#               "Height": 256,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             }
#           ]
#         },
#         "FrontCameraRecord": {
#           "X": 1,
#           "Y": 0,
#           "Z": 0,
#           "Pitch": 0,
#           "Roll": 0,
#           "Yaw": 0,
#           "CaptureSettings": [
#             {
#               "ImageType": 0,
#               "Width": 1024,
#               "Height": 1024,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             },
#             {
#               "ImageType": 2,
#               "Width": 1024,
#               "Height": 1024,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             }
#           ]
#         },
#         "DownCameraRecord": {
#           "X": 0,
#           "Y": 0,
#           "Z": 0,
#           "Pitch": -90,
#           "Roll": 0,
#           "Yaw": 0,
#           "CaptureSettings": [
#             {
#               "ImageType": 0,
#               "Width": 1024,
#               "Height": 1024,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             },
#             {
#               "ImageType": 2,
#               "Width": 1024,
#               "Height": 1024,
#               "FOV_Degrees": 90,
#               "AutoExposureMaxBrightness": 1,
#               "AutoExposureMinBrightness": 0.03
#             }
#           ]
#         }
#       },
#       "Sensors": {
#           "Imu": {
#                 "SensorType": 2,
#                 "Enabled" : True,
#                 "AngularRandomWalk": 0.3,
#                 "GyroBiasStabilityTau": 500,
#                 "GyroBiasStability": 4.6,
#                 "VelocityRandomWalk": 0.24,
#                 "AccelBiasStabilityTau": 800,
#                 "AccelBiasStability": 36
#             }
#       }
#     }
#   }
# }

# env_exec_path_dict = {
#     "NYCEnvironmentMegapa": {
#         'bash_name': 'NYCEnvironmentMegapa',
#         'exec_path': './closeloop_envs',
#     },
#     "TropicalIsland": {
#         'bash_name': 'TropicalIsland',
#         'exec_path': './closeloop_envs',
#     },
#     "NewYorkCity": {
#         'bash_name': 'NewYorkCity',
#         'exec_path': './closeloop_envs',
#     },
#     "ModularPark": {
#         'bash_name': 'ModularPark',
#         'exec_path': './closeloop_envs',
#     },
#     "ModularEuropean": {
#         'bash_name': 'ModularEuropean',
#         'exec_path': './closeloop_envs',
#     },
#     "ModernCityMap": {
#         'bash_name': 'ModernCityMap',
#         'exec_path': './closeloop_envs',
#     },
#     "Carla_Town01": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town01/LinuxNoEditor',
#     },
#     "Carla_Town02": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town02/LinuxNoEditor',
#     },
#     "Carla_Town03": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town03/LinuxNoEditor',
#     },
#     "Carla_Town04": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town04/LinuxNoEditor',
#     },
#     "Carla_Town05": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town05/LinuxNoEditor',
#     },
#     "Carla_Town06": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town06/LinuxNoEditor',
#     },
#     "Carla_Town07": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town07/LinuxNoEditor',
#     },
#     "Carla_Town10HD": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town10HD/LinuxNoEditor',
#     },
#     "Carla_Town15": {
#         'bash_name': 'CarlaUE4',
#         'exec_path': './carla_town_envs/Town15/LinuxNoEditor',
#     },
# }
# def create_drones(drone_num_per_env=1, show_scene=False, uav_mode=True) -> dict:
#     airsim_settings = copy.deepcopy(AIRSIM_SETTINGS_TEMPLATE)
#     return airsim_settings


# def pid_exists(pid) -> bool:
#     """
#     Check whether pid exists in the current process table.
#     UNIX only.
#     """
#     if pid < 0:
#         return False

#     try:
#         os.kill(pid, 0)
#     except OSError as err:
#         if err.errno == errno.ESRCH:
#             # ESRCH == No such process
#             return False
#         elif err.errno == errno.EPERM:
#             # EPERM clearly means there's a process to deny access to
#             return True
#         else:
#             # According to "man 2 kill" possible error values are
#             # (EINVAL, EPERM, ESRCH)
#             raise
#     else:
#         return True


# def FromPortGetPid(port: int):
#     subprocess_execute = "netstat -nlp | grep {}".format(
#         port,
#     )

#     try:
#         p = subprocess.Popen(
#             subprocess_execute,
#             stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
#             shell=True,
#         )
#     except Exception as e:
#         print(
#             "{}\t{}\t{}".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#                 'FromPortGetPid',
#                 e,
#             )
#         )
#         return None
#     except:
#         return None

#     pid = None
#     for line in iter(p.stdout.readline, b''):
#         line = str(line, encoding="utf-8")
#         if 'tcp' in line:
#             pid = line.strip().split()[-1].split('/')[0]
#             try:
#                 pid = int(pid)
#             except:
#                 pid = None
#             break

#     try:
#         os.kill(p.pid, signal.SIGKILL)
#     except:
#         pass

#     return pid


# def KillPid(pid) -> None:
#     if pid is None or not isinstance(pid, int):
#         return

#     while pid_exists(pid):
#         try:
#             print('pid {} is killed'.format(pid))
#             os.kill(pid, signal.SIGKILL)
#         except Exception as e:
#             pass
#         time.sleep(0.5)

#     return


# def KillPorts(ports) -> None:
#     threads = []

#     def _kill_port(index, port):
#         pid = FromPortGetPid(port)
#         KillPid(pid)

#     for index, port in enumerate(ports):
#         thread = threading.Thread(target=_kill_port, args=(index, port), daemon=True)
#         threads.append(thread)
#     for thread in threads:
#         thread.start()
#     for thread in threads:
#         thread.join()
#     threads = []

#     return


# def KillAirVLN() -> None:
#     subprocess_execute = "pkill -9 AirVLN"

#     try:
#         p = subprocess.Popen(
#             subprocess_execute,
#             stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
#             shell=True,
#         )
#     except Exception as e:
#         print(
#             "{}\t{}\t{}".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#                 'KillAirVLN',
#                 e,
#             )
#         )
#         return
#     except:
#         return

#     try:
#         os.kill(p.pid, signal.SIGKILL)
#     except:
#         pass

#     time.sleep(1)
#     return


# class EventHandler(object):
#     def __init__(self):
#         scene_ports = []
#         for i in range(1000):
#             scene_ports.append(
#                 int(args.port) + (i+1)
#             )
#         self.scene_ports = scene_ports

#         scene_gpus = []
#         while len(scene_gpus) < 100:
#             scene_gpus += GPU_IDS.copy()
#         self.scene_gpus = scene_gpus

#         self.scene_used_ports = []
        
#         self.port_to_scene = {}

#     def ping(self) -> bool:
#         return True

#     def _open_scenes(self, ip: str , scen_id_gpu_list: list):
#         print(
#             "{}\t关闭场景中".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#             )
#         )
#         KillPorts(self.scene_used_ports)
#         self.scene_used_ports = []
#         print(
#             "{}\t已关闭所有场景".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#             )
#         )

#         # Occupied airsim port 1
#         ports = []
#         index = 0
#         while len(ports) < len(scen_id_gpu_list):
#             pid = FromPortGetPid(self.scene_ports[index])
#             if pid is None or not isinstance(pid, int):
#                 ports.append(self.scene_ports[index])
#             index += 1

#         KillPorts(ports)

#         # Occupied GPU 2
#         gpus = [scen_id_gpu_list[index][-1] for index in range(len(scen_id_gpu_list))]
#         print(scen_id_gpu_list)

#         # search scene path 3
#         choose_env_exe_paths = []
#         for scen_id, gpu_id in scen_id_gpu_list:
#             if str(scen_id).lower() == 'none':
#                 choose_env_exe_paths.append(None)
#                 continue
            
#             if scen_id in env_exec_path_dict:
#                 env_info = env_exec_path_dict.get(scen_id)
#                 res = os.path.join(args.root_path, env_info['exec_path'], env_info['bash_name'] + '.sh')
#                 choose_env_exe_paths.append(res)
#             else:
#                 prefix_flag = False
#                 for map_name in env_exec_path_dict.keys():
#                     if str(scen_id).startswith(map_name):
#                         prefix_flag = True
#                         env_info = env_exec_path_dict.get(map_name)
#                         res = os.path.join(args.root_path, env_info['exec_path'], env_info['bash_name'] + '.sh')
#                         choose_env_exe_paths.append(res)
#                 if not prefix_flag:
#                     print(f'can not find scene file: {scen_id}')
#                     raise KeyError

#         p_s = []
#         for index, (scen_id, gpu_id) in enumerate(scen_id_gpu_list):
#             # airsim settings 4
#             airsim_settings = create_drones()
#             airsim_settings['ApiServerPort'] = int(ports[index])
#             self.port_to_scene[ports[index]] = (scen_id, gpu_id)
#             airsim_settings_write_content = json.dumps(airsim_settings)
#             if not os.path.exists(str(CWD_DIR / 'settings' / str(ports[index]))):
#                 os.makedirs(str(CWD_DIR / 'settings' / str(ports[index])), exist_ok=True)
#             with open(str(CWD_DIR / 'settings' / str(ports[index]) / 'settings.json'), 'w', encoding='utf-8') as dump_f:
#                 dump_f.write(airsim_settings_write_content)

#             # open scene 5
#             if choose_env_exe_paths[index] is None:
#                 p_s.append(None)
#                 continue
#             else:
#                 subprocess_execute = "bash {} -RenderOffscreen -NoSound -NoVSync -GraphicsAdapter={} -settings={} ".format(
#                     choose_env_exe_paths[index],
#                     gpu_id,
#                     str(CWD_DIR / 'settings' / str(ports[index]) / 'settings.json'),
#                 )
#                 time.sleep(1)
#                 print(subprocess_execute)

#                 try:
#                     p = subprocess.Popen(
#                         subprocess_execute,
#                         stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
#                         shell=True,
#                     )
#                     p_s.append(p)
#                 except Exception as e:
#                     print(
#                         "{}\t{}".format(
#                             str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#                             e,
#                         )
#                     )
#                     return False, None
#                 except:
#                     return False, None
#         time.sleep(10)
#         self.scene_used_ports += copy.deepcopy(ports)
        
#         print("finished", ip)

#         return True, (ip, ports)
    
#     def reopen_scene_from_port(self, port):

#         KillPorts([port])
        
#         scene_id, gpu_id = self.port_to_scene[port]
#         env_info = env_exec_path_dict.get(scene_id)
#         env_path = os.path.join(args.root_path, env_info['exec_path'], env_info['bash_name'] + '.sh')
#         subprocess_execute = "bash {} -RenderOffscreen -NoSound -NoVSync -GraphicsAdapter={} -settings={} ".format(
#                     env_path,
#                     gpu_id,
#                     str(CWD_DIR / 'settings' / str(port) / 'settings.json'),
#                 )
#         time.sleep(1)
#         print(subprocess_execute)
        
#         p = subprocess.Popen(
#                         subprocess_execute,
#                         stdin=None, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
#                         shell=True,
#                     )
        
#     def reopen_scenes(self, ip: str, scen_id_gpu_list: list):
#         print(
#             "{}\tSTART reopen_scenes".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#             )
#         )
#         try:
#             print(scen_id_gpu_list)
#             ip = ip
#             for item in scen_id_gpu_list:
#                 try:
#                     item[0] = item[0]
#                 except:
#                     pass
#                 # item[0] = item[0].decode('utf-8')
#             result = self._open_scenes(ip, scen_id_gpu_list)
#         except Exception as e:
#             print(e)
#             exe_type, exe_value, exe_traceback = sys.exc_info()
#             exe_info_list = traceback.format_exception(
#                 exe_type, exe_value, exe_traceback)
#             tracebacks = ''.join(exe_info_list)
#             print('traceback:', tracebacks)
#             result = False, None
#         print(
#             "{}\tEND reopen_scenes".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#             )
#         )
#         return result

#     def close_scenes(self, ip: str) -> bool:
#         print(
#             "{}\tSTART close_scenes".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#             )
#         )

#         try:
#             KillPorts(self.scene_used_ports)
#             self.scene_used_ports = []

#             result = True
#         except Exception as e:
#             print(e)
#             result = False

#         print(
#             "{}\tEND close_scenes".format(
#                 str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
#             )
#         )
#         return result


# def serve_background(server, daemon=False):
#     def _start_server(server):
#         server.start()
#         server.close()

#     t = threading.Thread(target=_start_server, args=(server,))
#     t.setDaemon(daemon)
#     t.start()
#     return t


# def serve(daemon=False):
#     try:
#         server = msgpackrpc.Server(EventHandler())
#         addr = msgpackrpc.Address(HOST, PORT)
#         server.listen(addr)

#         thread = serve_background(server, daemon)

#         return addr, server, thread
#     except Exception as err:
#         print("error",err)
#         pass


# if __name__ == '__main__':
#     # Argument
#     parser = argparse.ArgumentParser()
#     parser.add_argument(
#         "--gpus",
#         type=str,
#         default='1,2,3,4',
#     )
#     parser.add_argument(
#         "--port",
#         type=int,
#         default=30000,
#         help='server port'
#     ) 
#     parser.add_argument(
#         "--root_path",
#         type=str,
#         default="/nfs/airport/airdrone/",
#         help='root dir for env path'
#     ) 
#     args = parser.parse_args()


#     HOST = '127.0.0.1'
#     PORT = int(args.port)
#     CWD_DIR = Path(str(os.path.abspath(__file__))).parent.resolve()
#     PROJECT_ROOT_DIR = CWD_DIR.parent
#     print("PROJECT_ROOT_DIR",PROJECT_ROOT_DIR)

#     gpu_list = []
#     gpus = str(args.gpus).split(',') 
#     for gpu in gpus:
#         gpu_list.append(int(gpu.strip()))
#     GPU_IDS = gpu_list.copy()


#     addr, server, thread = serve()
#     print(f"start listening \t{addr._host}:{addr._port}")
















import argparse
import threading
import traceback
import msgpackrpc
from pathlib import Path
import time
import os
import json
import sys
import subprocess
import errno
import signal
import copy
import socket
import shutil
import atexit


AIRSIM_SETTINGS_TEMPLATE = {
    "SeeDocsAt": "https://microsoft.github.io/AirSim/settings/",
    "SettingsVersion": 1.2,
    "SimMode": "Multirotor",
    "ClockSpeed": 10,
    "ViewMode": "NoDisplay",
    "PhysiceEngineName": "ExternalPhysicsEngine",
    "Recording": {"RecordInterval": 1, "Enabled": False, "Cameras": []},
    "Vehicles": {
        "Drone_1": {
            "VehicleType": "SimpleFlight",
            "UseSerial": False,
            "LockStep": True,
            "AutoCreate": True,
            "X": 0, "Y": 0, "Z": 0,
            "Roll": 0, "Pitch": 0, "Yaw": 0,
            "Cameras": {
                "FrontCamera": {
                    "X": 1, "Y": 0, "Z": 0, "Pitch": 0, "Roll": 0, "Yaw": 0,
                    "CaptureSettings": [
                        {"ImageType": 0, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                        {"ImageType": 2, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                    ],
                },
                "RearCamera": {
                    "X": -1, "Y": 0, "Z": 0, "Pitch": 0, "Roll": 0, "Yaw": 180,
                    "CaptureSettings": [
                        {"ImageType": 0, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                        {"ImageType": 2, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                    ],
                },
                "LeftCamera": {
                    "X": 0, "Y": -1, "Z": 0, "Pitch": 0, "Roll": 0, "Yaw": -90,
                    "CaptureSettings": [
                        {"ImageType": 0, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                        {"ImageType": 2, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                    ],
                },
                "RightCamera": {
                    "X": 0, "Y": 1, "Z": 0, "Pitch": 0, "Roll": 0, "Yaw": 90,
                    "CaptureSettings": [
                        {"ImageType": 0, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                        {"ImageType": 2, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                    ],
                },
                "DownCamera": {
                    "X": 0, "Y": 0, "Z": 0, "Pitch": -90, "Roll": 0, "Yaw": 0,
                    "CaptureSettings": [
                        {"ImageType": 0, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                        {"ImageType": 2, "Width": 256, "Height": 256, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                    ],
                },
                "FrontCameraRecord": {
                    "X": 1, "Y": 0, "Z": 0, "Pitch": 0, "Roll": 0, "Yaw": 0,
                    "CaptureSettings": [
                        {"ImageType": 0, "Width": 1024, "Height": 1024, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                        {"ImageType": 2, "Width": 1024, "Height": 1024, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                    ],
                },
                "DownCameraRecord": {
                    "X": 0, "Y": 0, "Z": 0, "Pitch": -90, "Roll": 0, "Yaw": 0,
                    "CaptureSettings": [
                        {"ImageType": 0, "Width": 1024, "Height": 1024, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                        {"ImageType": 2, "Width": 1024, "Height": 1024, "FOV_Degrees": 90,
                         "AutoExposureMaxBrightness": 1, "AutoExposureMinBrightness": 0.03},
                    ],
                },
            },
            "Sensors": {
                "Imu": {
                    "SensorType": 2,
                    "Enabled": True,
                    "AngularRandomWalk": 0.3,
                    "GyroBiasStabilityTau": 500,
                    "GyroBiasStability": 4.6,
                    "VelocityRandomWalk": 0.24,
                    "AccelBiasStabilityTau": 800,
                    "AccelBiasStability": 36,
                }
            },
        }
    },
}

env_exec_path_dict = {
    "NYCEnvironmentMegapa": {"bash_name": "NYCEnvironmentMegapa",
                            "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/closeloop_envs"},
    "TropicalIsland": {"bash_name": "TropicalIsland",
                       "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/closeloop_envs"},
    "NewYorkCity": {"bash_name": "NewYorkCity",
                    "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/closeloop_envs"},
    "ModularPark": {"bash_name": "ModularPark",
                    "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/closeloop_envs"},
    "ModularEuropean": {"bash_name": "ModularEuropean",
                        "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/closeloop_envs"},
    "ModernCityMap": {"bash_name": "ModernCityMap",
                      "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/closeloop_envs"},
    "Carla_Town01": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town01/LinuxNoEditor"},
    "Carla_Town02": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town02/LinuxNoEditor"},
    "Carla_Town03": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town03/LinuxNoEditor"},
    "Carla_Town04": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town04/LinuxNoEditor"},
    "Carla_Town05": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town05/LinuxNoEditor"},
    "Carla_Town06": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town06/LinuxNoEditor"},
    "Carla_Town07": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town07/LinuxNoEditor"},
    "Carla_Town10HD": {"bash_name": "CarlaUE4",
                       "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town10HD/LinuxNoEditor"},
    "Carla_Town15": {"bash_name": "CarlaUE4",
                     "exec_path": "/share-global/tmp/xcl/TravelUAV-main/TravelUAV_env/carla_town_envs/Town15/LinuxNoEditor"},
}


def create_drones(drone_num_per_env=1, show_scene=False, uav_mode=True) -> dict:
    airsim_settings = copy.deepcopy(AIRSIM_SETTINGS_TEMPLATE)
    return airsim_settings


def pid_exists(pid) -> bool:
    if pid < 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
        elif err.errno == errno.EPERM:
            return True
        else:
            raise
    else:
        return True


def FromPortGetPid(port: int):
    subprocess_execute = "netstat -nlp | grep {}".format(port)
    try:
        p = subprocess.Popen(
            subprocess_execute,
            stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            shell=True,
        )
    except Exception as e:
        print("{}\t{}\t{}".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                                 'FromPortGetPid', e))
        return None

    pid = None
    for line in iter(p.stdout.readline, b''):
        try:
            line = str(line, encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if 'tcp' in line:
            pid = line.strip().split()[-1].split('/')[0]
            try:
                pid = int(pid)
            except Exception:
                pid = None
            break

    try:
        os.kill(p.pid, signal.SIGKILL)
    except Exception:
        pass

    return pid


def KillPid(pid) -> None:
    if pid is None or not isinstance(pid, int):
        return
    while pid_exists(pid):
        try:
            print('pid {} is killed'.format(pid))
            os.kill(pid, signal.SIGKILL)
        except Exception:
            pass
        time.sleep(0.5)


def KillPorts(ports) -> None:
    threads = []

    def _kill_port(index, port):
        pid = FromPortGetPid(port)
        KillPid(pid)

    for index, port in enumerate(ports):
        thread = threading.Thread(target=_kill_port, args=(index, port), daemon=True)
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def KillAirVLN() -> None:
    subprocess_execute = "pkill -9 AirVLN"
    try:
        p = subprocess.Popen(
            subprocess_execute,
            stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            shell=True,
        )
    except Exception as e:
        print("{}\t{}\t{}".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
                                 'KillAirVLN', e))
        return

    try:
        os.kill(p.pid, signal.SIGKILL)
    except Exception:
        pass
    time.sleep(1)


# ----------------------------
# Headless robustness helpers
# ----------------------------
_XVFB_PROC = None


def _start_xvfb_if_needed():
    """
    In pure server/no-window/no-DISPLAY situations, UE/RenderOffscreen often still needs an X server.
    This starts Xvfb :99 automatically if DISPLAY is not set.
    """
    global _XVFB_PROC
    if os.environ.get("DISPLAY"):
        return

    xvfb = shutil.which("Xvfb")
    if xvfb is None:
        print("[WARNING] DISPLAY is empty and Xvfb not found. "
              "UE may hang or images may time out. Consider installing Xvfb.")
        return

    display = ":99"
    cmd = f"{xvfb} {display} -screen 0 1920x1080x24 -nolisten tcp"
    try:
        _XVFB_PROC = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        os.environ["DISPLAY"] = display
        print(f"[INFO] Started Xvfb on DISPLAY={display} (pid={_XVFB_PROC.pid})")

        def _cleanup():
            global _XVFB_PROC
            if _XVFB_PROC is not None:
                try:
                    os.killpg(os.getpgid(_XVFB_PROC.pid), signal.SIGKILL)
                except Exception:
                    pass
                _XVFB_PROC = None

        atexit.register(_cleanup)
    except Exception as e:
        print(f"[WARNING] Failed to start Xvfb: {e}")


def _wait_for_port(port, host="127.0.0.1", timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            try:
                if s.connect_ex((host, port)) == 0:
                    print(f"[INFO] ✅ Simulator ready on port {port}")
                    return True
            except Exception:
                pass
        time.sleep(1)
    print(f"[ERROR] ❌ Simulator not ready after {timeout}s on port {port}")
    return False


def _safe_decode(x):
    if isinstance(x, bytes):
        return x.decode("utf-8", errors="ignore")
    return str(x)


class EventHandler(object):
    def __init__(self):
        scene_ports = []
        for i in range(1000):
            scene_ports.append(int(args.port) + (i + 1))
        self.scene_ports = scene_ports

        scene_gpus = []
        while len(scene_gpus) < 100:
            scene_gpus += GPU_IDS.copy()
        self.scene_gpus = scene_gpus

        self.scene_used_ports = []
        self.port_to_scene = {}

        # Track launched UE processes for better cleanup (optional)
        self._scene_procs = {}

    def ping(self) -> bool:
        return True

    def _open_scenes(self, ip: str, scen_id_gpu_list: list):
        # Ensure DISPLAY exists for headless server (important for nohup background)
        _start_xvfb_if_needed()

        # -------- Step 0. IP类型修正 --------
        ip = _safe_decode(ip)

        print("{}\t关闭场景中".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
        KillPorts(self.scene_used_ports)
        self.scene_used_ports = []
        self._scene_procs = {}
        print("{}\t已关闭所有场景".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))

        # -------- Step 1. 占用端口 --------
        ports = []
        index = 0
        while len(ports) < len(scen_id_gpu_list):
            pid = FromPortGetPid(self.scene_ports[index])
            if pid is None or not isinstance(pid, int):
                ports.append(self.scene_ports[index])
            index += 1
        KillPorts(ports)

        # -------- Step 2. 读取 GPU --------
        gpus = [scen_id_gpu_list[idx][-1] for idx in range(len(scen_id_gpu_list))]
        print("[DEBUG] scen_id_gpu_list:", scen_id_gpu_list)

        # -------- Step 3. 查找场景路径 --------
        choose_env_exe_paths = []
        scen_id_str_list = []
        for scen_id, gpu_id in scen_id_gpu_list:
            scen_id_str = _safe_decode(scen_id)
            scen_id_str_list.append(scen_id_str)

            if scen_id_str.lower() == 'none':
                choose_env_exe_paths.append(None)
                continue

            if scen_id_str in env_exec_path_dict:
                env_info = env_exec_path_dict.get(scen_id_str)
                res = os.path.join(args.root_path, env_info['exec_path'], env_info['bash_name'] + '.sh')
                choose_env_exe_paths.append(res)
            else:
                prefix_flag = False
                for map_name in env_exec_path_dict.keys():
                    if scen_id_str.startswith(map_name):
                        prefix_flag = True
                        env_info = env_exec_path_dict.get(map_name)
                        res = os.path.join(args.root_path, env_info['exec_path'], env_info['bash_name'] + '.sh')
                        choose_env_exe_paths.append(res)
                        break
                if not prefix_flag:
                    print(f'[ERROR] can not find scene file: {scen_id_str}')
                    raise KeyError

        # -------- Step 4. 创建 AirSim 配置文件 & 启动 UE --------
        p_s = []
        for idx, (scen_id, gpu_id) in enumerate(scen_id_gpu_list):
            airsim_settings = create_drones()
            airsim_settings['ApiServerPort'] = int(ports[idx])

            scen_id_str = scen_id_str_list[idx]
            self.port_to_scene[ports[idx]] = (scen_id_str, gpu_id)

            settings_dir = CWD_DIR / 'settings' / str(ports[idx])
            os.makedirs(settings_dir, exist_ok=True)
            settings_path = settings_dir / 'settings.json'
            with open(settings_path, 'w', encoding='utf-8') as dump_f:
                dump_f.write(json.dumps(airsim_settings))

            if choose_env_exe_paths[idx] is None:
                p_s.append(None)
                continue

            # --- IMPORTANT: log per port (avoid inheriting broken stdio under nohup) ---
            log_dir = CWD_DIR / "ue_logs"
            os.makedirs(log_dir, exist_ok=True)
            log_path = log_dir / f"ue_{scen_id_str}_{ports[idx]}.log"
            log_f = open(log_path, "ab", buffering=0)

            # --- UE command ---
            subprocess_execute = (
                f"bash {choose_env_exe_paths[idx]} "
                f"-RenderOffscreen -NoSound -NoVSync -GraphicsAdapter={gpu_id} -settings={settings_path}"
            )
            print(f"\n[DEBUG] 打开场景命令: {subprocess_execute}")
            print(f"[DEBUG] 检查场景脚本路径是否存在: {choose_env_exe_paths[idx]} -> {os.path.exists(choose_env_exe_paths[idx])}")
            print(f"[DEBUG] settings.json 是否存在: {os.path.exists(settings_path)}")
            print(f"[DEBUG] UE log: {log_path}")
            print(f"[DEBUG] DISPLAY={os.environ.get('DISPLAY','')}")

            try:
                # start_new_session=True to isolate from nohup/terminal, also helps killpg.
                p = subprocess.Popen(
                    subprocess_execute,
                    stdin=subprocess.DEVNULL,
                    stdout=log_f,
                    stderr=log_f,
                    shell=True,
                    start_new_session=True,
                    env=os.environ.copy(),
                )
                p_s.append(p)
                self._scene_procs[ports[idx]] = (p, log_f)
                print(f"[DEBUG] 场景 {scen_id_str} 启动中 (pid={p.pid})，等待端口就绪...")
            except Exception as e:
                print("[ERROR] 启动命令执行失败:", e)
                try:
                    log_f.close()
                except Exception:
                    pass
                return False, None

            # 不要固定 sleep 70：用端口探测更稳
            _wait_for_port(ports[idx], host="127.0.0.1", timeout=120)

        time.sleep(2)

        # -------- Step 5. 最终确认端口 --------
        all_ok = True
        for port in ports:
            all_ok = _wait_for_port(port, host="127.0.0.1", timeout=20) and all_ok

        self.scene_used_ports += copy.deepcopy(ports)
        print(f"[INFO] finished opening scenes on {ip}, ok={all_ok}")
        return True, (ip, ports)

    def reopen_scene_from_port(self, port):
        _start_xvfb_if_needed()

        KillPorts([port])

        scene_id, gpu_id = self.port_to_scene[port]
        env_info = env_exec_path_dict.get(scene_id)
        env_path = os.path.join(args.root_path, env_info['exec_path'], env_info['bash_name'] + '.sh')
        settings_path = str(CWD_DIR / 'settings' / str(port) / 'settings.json')

        cmd = f"bash {env_path} -RenderOffscreen -NoSound -NoVSync -GraphicsAdapter={gpu_id} -settings={settings_path}"
        print(cmd)

        log_dir = CWD_DIR / "ue_logs"
        os.makedirs(log_dir, exist_ok=True)
        log_path = log_dir / f"ue_reopen_{scene_id}_{port}.log"
        log_f = open(log_path, "ab", buffering=0)

        p = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=log_f,
            stderr=log_f,
            shell=True,
            start_new_session=True,
            env=os.environ.copy(),
        )
        self._scene_procs[port] = (p, log_f)
        _wait_for_port(port, host="127.0.0.1", timeout=120)

    def reopen_scenes(self, ip: str, scen_id_gpu_list: list):
        print("{}\tSTART reopen_scenes".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
        try:
            # decode bytes early to avoid msgpack decode surprises later
            fixed = []
            for scen_id, gpu_id in scen_id_gpu_list:
                fixed.append((_safe_decode(scen_id), int(gpu_id)))
            # keep original structure expected by _open_scenes: list of pairs
            scen_id_gpu_list_fixed = [(sid, gid) for sid, gid in fixed]
            result = self._open_scenes(ip, scen_id_gpu_list_fixed)
        except Exception as e:
            print(e)
            exe_type, exe_value, exe_traceback = sys.exc_info()
            tracebacks = ''.join(traceback.format_exception(exe_type, exe_value, exe_traceback))
            print('traceback:', tracebacks)
            result = False, None
        print("{}\tEND reopen_scenes".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
        return result

    def close_scenes(self, ip: str) -> bool:
        print("{}\tSTART close_scenes".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
        try:
            KillPorts(self.scene_used_ports)
            self.scene_used_ports = []

            # close logs
            for port, (p, log_f) in list(self._scene_procs.items()):
                try:
                    # kill process group
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except Exception:
                    pass
                try:
                    log_f.close()
                except Exception:
                    pass
            self._scene_procs = {}

            result = True
        except Exception as e:
            print(e)
            result = False
        print("{}\tEND close_scenes".format(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))))
        return result


def serve_background(server, daemon=False):
    def _start_server(server):
        server.start()
        server.close()

    t = threading.Thread(target=_start_server, args=(server,))
    t.setDaemon(daemon)
    t.start()
    return t


def serve(daemon=False):
    try:
        server = msgpackrpc.Server(EventHandler())
        addr = msgpackrpc.Address(HOST, PORT)
        server.listen(addr)
        thread = serve_background(server, daemon)
        return addr, server, thread
    except Exception as err:
        print("error", err)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpus", type=str, default='1,2,3,4')
    parser.add_argument("--port", type=int, default=30000, help='server port')
    parser.add_argument("--root_path", type=str, default="/nfs/airport/airdrone/", help='root dir for env path')
    args = parser.parse_args()

    HOST = '127.0.0.1'
    PORT = int(args.port)
    CWD_DIR = Path(str(os.path.abspath(__file__))).parent.resolve()
    PROJECT_ROOT_DIR = CWD_DIR.parent
    print("PROJECT_ROOT_DIR", PROJECT_ROOT_DIR)

    gpu_list = []
    gpus = str(args.gpus).split(',')
    for gpu in gpus:
        gpu_list.append(int(gpu.strip()))
    GPU_IDS = gpu_list.copy()

    # Make headless background robust: ensure DISPLAY exists (Xvfb) before serving.
    _start_xvfb_if_needed()

    addr, server, thread = serve()
    print(f"start listening \t{addr._host}:{addr._port}")
