"""High level commands for interacting with the PLC.

The handler converts application requests into register writes and
communicates them through ``write_to_plc``. Errors such as unsupported
commands are reported via the ``error`` signal.
"""

import logging

from PyQt6.QtCore import QObject, pyqtSignal as Signal

CONTROL_BITS = {
    "power_on": 0,
    "reset_torque": 4,
    "reset_angle": 5,
    "write_retain": 6,
    "reset_error": 7,
    "reset_alarm": 8,
}
CONTROL_CMD = {
    "halt": 0b000,
    "jog_cw": 0b001,
    "jog_ccw": 0b010,
    "torque_hold": 0b011,
    "move_to_angle": 0b100,
    "stop": 0b111,
}

class CommandHandler(QObject):
    """Dispatches control commands to the PLC.

    Signals
    -------
    write_to_plc: dict
        Emitted with the Modbus register dictionary when a command should
        be sent to the PLC.
    error: str
        Emitted when an invalid command argument is provided.
    """

    write_to_plc = Signal(dict)
    error = Signal(str)

    def __init__(self, parent=None):
        """Initialize the command handler and connect its signals."""
        super(CommandHandler, self).__init__(parent)
        self.parent = parent
        self.write_to_plc.connect(
            self.parent.realtime_data.modbus_registers_to_PLC_update
        )

    def set_plc_mode(self, mode):
        """Set the PLC operating mode.

        Parameters
        ----------
        mode: str
            One of ``'auto'``, ``'hand'`` or ``'service'``.

        Raises
        ------
        ValueError
            If ``mode`` is not supported. In this case the ``error`` signal
            is also emitted.
        """
        regs_ = self.parent.modbus_write_regs
        mask = 0b0001111111111111
        regs_['Modbus_CTRL'] &= mask
        match mode:
            case 'auto':
                mask = 0b0100000000000000
            case 'hand':
                mask = 0b0000000000000000
            case 'service':
                mask = 0b1000000000000000
            case 'hand_calibration':
                mask = 0b1010000000000000
            case _:
                message = f"Unsupported PLC mode: {mode}"
                logging.warning(message)
                self.error.emit(message)
                raise ValueError(message)
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def servo_power_on(self):
        """Turn on the servo drive."""
        self._set_control_bit(CONTROL_BITS["power_on"])

    def servo_power_off(self):
        """Turn off the servo drive."""
        self._clear_control_bit(CONTROL_BITS["power_on"])

    def reset_error(self):
        """Reset the servo drive error."""
        self._set_control_bit(CONTROL_BITS["reset_error"])

    def alarm_reset(self):
        """Turn off the alarm."""
        self._set_control_bit(CONTROL_BITS["reset_alarm"])

    def set_tension(self, tension=0, velocity=0):
        """Set the tension and velocity setpoints."""
        regs_ = self.parent.modbus_write_regs
        regs_['Modbus_TensionSV'] = tension
        regs_['Modbus_VelocitySV'] = velocity
        self.write_to_plc.emit(regs_)

    def torque_hold(self):
        self._do_command("torque_hold")

    def jog_cw(self):
        self._do_command("jog_cw")

    def jog_ccw(self):
        self._do_command("jog_ccw")

    def halt(self):
        """Halt motion"""
        self._do_command("halt")

    def stop(self):
        """Stop motion and reset setpoints to zero."""
        self._do_command("stop")

    def set_plc_register(self, name='Modbus_CTRL', value=0):
        """Write a raw value to a Modbus register."""
        regs_ = self.parent.modbus_write_regs
        regs_[name] = value
        self.write_to_plc.emit(regs_)

    def _do_command(self, command):
        regs_ = self.parent.modbus_write_regs
        # Создаём битовую маску по месту размещения управляющей команды в слове управления (биты с 1 по 3)
        mask = 0b111 << 1
        # Очищаем эти разряды в слове управления
        regs_['Modbus_CTRL'] &= ~mask
        # Устанавливаем новые значения
        regs_['Modbus_CTRL'] |= (CONTROL_CMD[command] << 1)
        # Отправляем в ПЛК
        self.write_to_plc.emit(regs_)

    def _set_control_bit(self, bit):
        regs_: dict = self.parent.modbus_write_regs
        regs_['Modbus_CTRL'] |= (1 << bit)
        self.write_to_plc.emit(regs_)

    def _clear_control_bit(self, bit):
        regs_: dict = self.parent.modbus_write_regs
        regs_['Modbus_CTRL'] &= ~(1 << bit)
        self.write_to_plc.emit(regs_)

    def clear_all_control_bits(self):
        """Clear all control bits."""
        regs_: dict = self.parent.modbus_write_regs
        for bit in CONTROL_BITS.values():
            regs_['Modbus_CTRL'] &= ~(1 << bit)
        self.write_to_plc.emit(regs_)