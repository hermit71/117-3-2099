"""High level commands for interacting with the PLC.

The handler converts application requests into register writes and
communicates them through ``write_to_plc``. Errors such as unsupported
commands are reported via the ``error`` signal.
"""

import logging

from PyQt6.QtCore import Qt, QObject, pyqtSignal as Signal, pyqtSlot as Slot


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
        mask = 0b0011111111111111
        regs_['Modbus_CTRL'] &= mask
        match mode:
            case 'auto':
                mask = 0b0100000000000000
            case 'hand':
                mask = 0b0000000000000000
            case 'service':
                mask = 0b1000000000000000
            case _:
                message = f"Unsupported PLC mode: {mode}"
                logging.warning(message)
                self.error.emit(message)
                raise ValueError(message)
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def servo_power_on(self):
        """Turn on the servo drive."""
        regs_ = self.parent.modbus_write_regs
        mask = 0b1111111111100000
        regs_['Modbus_CTRL'] &= mask
        mask = 0b0000000000000001
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def servo_power_off(self):
        """Turn off the servo drive."""
        regs_: dict = self.parent.modbus_write_regs
        mask = 0b1111111111100000
        regs_['Modbus_CTRL'] &= mask
        mask = 0b0000000000000000
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def set_tension(self, tension=0, velocity=0):
        """Set the tension and velocity setpoints."""
        regs_ = self.parent.modbus_write_regs
        regs_['Modbus_TensionSV'] = tension
        regs_['Modbus_VelocitySV'] = velocity
        mask = 0b1111111111100001
        regs_['Modbus_CTRL'] &= mask
        mask = 0b0000000000000010
        regs_['Modbus_CTRL'] |= mask
        self.write_to_plc.emit(regs_)

    def jog(self, direction='cw', velocity=0):
        """Jog the motor in a direction at the given velocity.

        Parameters
        ----------
        direction: str
            'cw' for clockwise or 'ccw' for counter-clockwise.
        velocity: int
            Velocity setpoint to send.

        Raises
        ------
        ValueError
            If ``direction`` is not one of the supported values. The
            ``error`` signal is also emitted.
        """
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
            case _:
                message = f"Unsupported jog direction: {direction}"
                logging.warning(message)
                self.error.emit(message)
                raise ValueError(message)
        self.write_to_plc.emit(regs_)

    def stop(self):
        """Stop motion and reset setpoints to zero."""
        regs_ = self.parent.modbus_write_regs
        regs_['Modbus_TensionSV'] = 0
        regs_['Modbus_VelocitySV'] = 0
        mask = 0b1111111111100001
        regs_['Modbus_CTRL'] &= mask
        self.write_to_plc.emit(regs_)

    def set_plc_register(self, name='Modbus_CTRL', value=0):
        """Write a raw value to a Modbus register."""
        regs_ = self.parent.modbus_write_regs
        regs_[name] = value
        self.write_to_plc.emit(regs_)
