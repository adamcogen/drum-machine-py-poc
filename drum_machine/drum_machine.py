from dao import DrumMachineDAO, LoopParams
from driver import DrumMachineThread
from gui import DrumMachineGUI, GUIStatus

def main():
        loop_params = LoopParams(2_500, 19)
        dao = DrumMachineDAO(loop_params)
        gui_status = GUIStatus()
        drum_thread = DrumMachineThread(dao, gui_status)
        gui = DrumMachineGUI(dao, gui_status)

main()