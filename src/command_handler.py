from PyQt6.QtCore import Qt, QObject, pyqtSignal as Signal, pyqtSlot as Slot

class CommandHandler(QObject):
    write_to_plc = Signal(dict)

    def __init__(self, parent=None):
        super(CommandHandler, self).__init__(parent)
        self.parent = parent
        self.write_to_plc.connect(self.parent.realtime_data.modbus_registers_to_PLC_update)

    def set_plc_mode(self, mode):
        regs_ = self.parent.modbus_write_regs
        mask = 0b0011111111111111
        regs_['Modbus_CTRL'] &= mask
        match mode:
            case 'auto':
                mask = 0b0100000000000000
            case 'hand':
                mask = 0b0000000000000000
            case 'service':
                mask = 0b1000000000000000
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def servo_power_on(self):
        regs_ = self.parent.modbus_write_regs
        mask = 0b1111111111100000
        regs_['Modbus_CTRL'] &= mask
        mask = 0b0000000000000001
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def servo_power_off(self):
        regs_: dict = self.parent.modbus_write_regs
        mask = 0b1111111111100000
        regs_['Modbus_CTRL'] &= mask
        mask = 0b0000000000000000
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def set_tension(self, tension=0, velocity=0):
        regs_ = self.parent.modbus_write_regs
        regs_['Modbus_TensionSV'] = tension
        regs_['Modbus_VelocitySV'] = velocity
        mask = 0b1111111111100001
        regs_['Modbus_CTRL'] &= mask
        mask = 0b0000000000000010
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def jog(self, direction='cw', velocity=0):
        regs_: dict = self.parent.modbus_write_regs
        regs_['Modbus_VelocitySV'] = velocity
        mask = 0b1111111111100001
        regs_['Modbus_CTRL'] &= mask
        match direction:
            case 'cw':
                mask = 0b0000000000000100
                regs_['Modbus_CTRL'] |= mask
            case 'ccw':
                mask = 0b0000000000001000
                regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def stop(self):
        regs_ = self.parent.modbus_write_regs
        regs_['Modbus_TensionSV'] = 0
        regs_['Modbus_VelocitySV'] = 0
        mask = 0b1111111111100001
        regs_['Modbus_CTRL'] &= mask
        self.write_to_plc.emit(regs_)

    def set_plc_register(self, name='Modbus_CTRL', value=0):
        regs_ = self.parent.modbus_write_regs
        regs_[name] = value
        self.write_to_plc.emit(regs_)