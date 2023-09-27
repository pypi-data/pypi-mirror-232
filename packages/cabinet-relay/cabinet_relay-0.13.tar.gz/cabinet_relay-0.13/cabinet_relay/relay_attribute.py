from typing import NamedTuple


class DigitalSource(NamedTuple):
    """
    继电器卡1通讯数字音源
    """
    slave_address: int = 1
    SPDIF: int = 0
    A2B_1: int = 1
    A2B_2: int = 2
    A2B_3: int = 3
    A2B_Power: int = 4
    P203_7_ACC_IN: int = 5
    EP_ACC_IN: int = 6
    A2B_4: int = 7
    CAN: int = 8
    Ohm_120: int = 9


class AnalogOutput(NamedTuple):
    """
    继电器卡2模拟输出
    """
    slave_address: int = 2
    DMM_I: int = 0
    Batt: int = 1
    Batt_Sence: int = 2
    ACC: int = 3
    HY_PWY: int = 4
    ACC_Turnon: int = 5
    AO_ON: int = 6
    CMRR_ON: int = 7
    A0_1: int = 8
    A0_2: int = 9
    A0_3: int = 10
    A0_4: int = 11


class StartupTime(NamedTuple):
    '''
    继电器卡3启动时间
    '''
    slave_address: int = 3
    Turnon_CH1: int = 0
    Turnon_CH2: int = 1
    Turnon_CH3: int = 2
    Turnon_CH4: int = 3
    Turnon_CH5: int = 4
    Turnon_CH6: int = 5
    Turnon_CH7: int = 6
    Turnon_CH8: int = 7
    Turnon_CAN: int = 8
    Turnon_ACC: int = 9
    Check_AO: int = 11
    DMM_V: int = 14
    LAN: int = 15


class SignalConditioningBoOne(NamedTuple):
    '''
    信号调理箱-CH1-8-CH17-24
    '''
    slave_address: int = 4
    CH1_AI_0: int = 0
    CH2_AI_0: int = 1
    CH3_AI_0: int = 2
    CH4_AI_0: int = 3
    CH5_AI_0: int = 4
    CH6_AI_0: int = 5
    CH7_AI_0: int = 6
    CH8_AI_0: int = 7
    CH1_AI_1: int = 8
    CH2_AI_1: int = 9
    CH3_AI_1: int = 10
    CH4_AI_1: int = 11
    CH5_AI_1: int = 12
    CH6_AI_1: int = 13
    CH7_AI_1: int = 14
    CH8_AI_1: int = 15


class SignalConditioningBoxTwo(NamedTuple):
    '''
    信号调理箱-CH1-8-CH17-24
    '''
    slave_address: int = 5
    CH9_AI_0: int = 0
    CH10_AI_0: int = 1
    CH11_AI_0: int = 2
    CH12_AI_0: int = 3
    CH13_AI_0: int = 4
    CH14_AI_0: int = 5
    CH15_AI_0: int = 6
    CH16_AI_0: int = 7
    CH9_AI_1: int = 8
    CH10_AI_1: int = 9
    CH11_AI_1: int = 10
    CH12_AI_1: int = 11
    CH13_AI_1: int = 12
    CH14_AI_1: int = 13
    CH15_AI_1: int = 14
    CH16_AI_1: int = 15


class SignalConditioningBoxThree(NamedTuple):
    '''
    信号调理箱-CH9-16-CH25-32
    '''
    slave_address: int = 6
    CH17_AI_0: int = 0
    CH18_AI_0: int = 1
    CH19_AI_0: int = 2
    CH20_AI_0: int = 3
    CH21_AI_0: int = 4
    CH22_AI_0: int = 5
    CH23_AI_0: int = 6
    CH24_AI_0: int = 7
    CH17_AI_1: int = 8
    CH18_AI_1: int = 9
    CH19_AI_1: int = 10
    CH20_AI_1: int = 11
    CH21_AI_1: int = 12
    CH22_AI_1: int = 13
    CH23_AI_1: int = 14
    CH24_AI_1: int = 15


class SignalConditioningBoxFour(NamedTuple):
    '''
    信号调理箱-CH9-16-CH25-32
    '''
    slave_address: int = 7
    CH25_AI_0: int = 0
    CH26_AI_0: int = 1
    CH27_AI_0: int = 2
    CH28_AI_0: int = 3
    CH29_AI_0: int = 4
    CH30_AI_0: int = 5
    CH31_AI_0: int = 6
    CH32_AI_0: int = 7
    CH25_AI_1: int = 8
    CH26_AI_1: int = 9
    CH27_AI_1: int = 10
    CH28_AI_1: int = 11
    CH29_AI_1: int = 12
    CH30_AI_1: int = 13
    CH31_AI_1: int = 14
    CH32_AI_1: int = 15


class LoadBoxCh1(NamedTuple):
    '''
    负载箱1-CH1/1
    '''
    slave_address: int = 8
    CH1_Res2: int = 0
    CH1_Res4: int = 1
    CH1_Res8: int = 2
    CH1_Res6: int = 3
    CH1_Res3: int = 4
    CH1_Res4_1: int = 5
    CH2_Res2: int = 6
    CH2_Res4: int = 7
    CH2_Res8: int = 8
    CH2_Res6: int = 9
    CH2_Res3: int = 10
    CH2_Res4_1: int = 11


class LoadBoxCh3(NamedTuple):
    '''
    负载箱1-CH3/4
    '''
    slave_address: int = 9
    CH3_Res2: int = 0
    CH3_Res4: int = 1
    CH3_Res8: int = 2
    CH3_Res6: int = 3
    CH3_Res3: int = 4
    CH3_Res4: int = 5
    CH4_Res2: int = 6
    CH4_Res4: int = 7
    CH4_Res8: int = 8
    CH4_Res6: int = 9
    CH4_Res3: int = 10
    CH4_Res4: int = 11


class LoadBoxCh5(NamedTuple):
    '''
    负载箱1-CH5/6
    '''
    slave_address: int = 10
    CH5_Res2: int = 0
    CH5_Res4: int = 1
    CH5_Res8: int = 2
    CH5_Res6: int = 3
    CH5_Res3: int = 4
    CH5_Res4: int = 5
    CH6_Res2: int = 6
    CH6_Res4: int = 7
    CH6_Res8: int = 8
    CH6_Res6: int = 9
    CH6_Res3: int = 10
    CH6_Res4: int = 11


class LoadBoxCh7(NamedTuple):
    '''
    负载箱1-CH7/8
    '''
    slave_address: int = 11
    CH7_Res2: int = 0
    CH7_Res4: int = 1
    CH7_Res8: int = 2
    CH7_Res6: int = 3
    CH7_Res3: int = 4
    CH7_Res4: int = 5
    CH8_Res2: int = 6
    CH8_Res4: int = 7
    CH8_Res8: int = 8
    CH8_Res6: int = 9
    CH8_Res3: int = 10
    CH8_Res4: int = 11


class LoadBoxCh9(NamedTuple):
    '''
    负载箱1-CH9/10
    '''
    slave_address: int = 12
    CH9_Res2: int = 0
    CH9_Res4: int = 1
    CH9_Res8: int = 2
    CH9_Res6: int = 3
    CH9_Res3: int = 4
    CH9_Res4: int = 5
    CH10_Res2: int = 6
    CH10_Res4: int = 7
    CH10_Res8: int = 8
    CH10_Res6: int = 9
    CH10_Res3: int = 10
    CH10_Res4: int = 11


class LoadBoxCh11(NamedTuple):
    '''
    负载箱1-CH11/12
    '''
    slave_address: int = 13
    CH11_Res2: int = 0
    CH11_Res4: int = 1
    CH11_Res8: int = 2
    CH11_Res6: int = 3
    CH11_Res3: int = 4
    CH11_Res4: int = 5
    CH12_Res2: int = 6
    CH12_Res4: int = 7
    CH12_Res8: int = 8
    CH12_Res6: int = 9
    CH12_Res3: int = 10
    CH12_Res4: int = 11


class LoadBoxCh13(NamedTuple):
    '''
    负载箱1-CH13/14
    '''
    slave_address: int = 14
    CH13_Res2: int = 0
    CH13_Res4: int = 1
    CH13_Res8: int = 2
    CH13_Res6: int = 3
    CH13_Res3: int = 4
    CH13_Res4: int = 5
    CH14_Res2: int = 6
    CH14_Res4: int = 7
    CH14_Res8: int = 8
    CH14_Res6: int = 9
    CH14_Res3: int = 10
    CH14_Res4: int = 11


class LoadBoxCh15(NamedTuple):
    '''
    负载箱1-CH15/16
    '''
    slave_address: int = 15
    CH15_Res2: int = 0
    CH15_Res4: int = 1
    CH15_Res8: int = 2
    CH15_Res6: int = 3
    CH15_Res3: int = 4
    CH15_Res4: int = 5
    CH16_Res2: int = 6
    CH16_Res4: int = 7
    CH16_Res8: int = 8
    CH16_Res6: int = 9
    CH16_Res3: int = 10
    CH16_Res4: int = 11


class ResistanceMeasurementOne(NamedTuple):
    '''
    负载箱1-电阻测量
    '''
    slave_address: int = 16


class ResistanceMeasurementTwoCh1(NamedTuple):
    '''
    负载箱2-CH1/1
    '''
    slave_address: int = 17
    CH17_Res2: int = 0
    CH17_Res4: int = 1
    CH17_Res8: int = 2
    CH17_Res6: int = 3
    CH17_Res3: int = 4
    CH17_Res4: int = 5
    CH18_Res2: int = 6
    CH18_Res4: int = 7
    CH18_Res8: int = 8
    CH18_Res6: int = 9
    CH18_Res3: int = 10
    CH18_Res4: int = 11


class ResistanceMeasurementTwoCh3(NamedTuple):
    '''
    负载箱2-CH3/4
    '''
    slave_address: int = 18
    CH19_Res2: int = 0
    CH19_Res4: int = 1
    CH19_Res8: int = 2
    CH19_Res6: int = 3
    CH19_Res3: int = 4
    CH19_Res4: int = 5
    CH20_Res2: int = 6
    CH20_Res4: int = 7
    CH20_Res8: int = 8
    CH20_Res6: int = 9
    CH20_Res3: int = 10
    CH20_Res4: int = 11


class ResistanceMeasurementTwoCh5(NamedTuple):
    '''
    负载箱2-CH5/6
    '''
    slave_address: int = 19
    CH21_Res2: int = 0
    CH21_Res4: int = 1
    CH21_Res8: int = 2
    CH21_Res6: int = 3
    CH21_Res3: int = 4
    CH21_Res4: int = 5
    CH22_Res2: int = 6
    CH22_Res4: int = 7
    CH22_Res8: int = 8
    CH22_Res6: int = 9
    CH22_Res3: int = 10
    CH22_Res4: int = 11


class ResistanceMeasurementTwoCh7(NamedTuple):
    '''
    负载箱2-CH7/8
    '''
    slave_address: int = 20
    CH23_Res2: int = 0
    CH23_Res4: int = 1
    CH23_Res8: int = 2
    CH23_Res6: int = 3
    CH23_Res3: int = 4
    CH23_Res4: int = 5
    CH24_Res2: int = 6
    CH24_Res4: int = 7
    CH24_Res8: int = 8
    CH24_Res6: int = 9
    CH24_Res3: int = 10
    CH24_Res4: int = 11


class ResistanceMeasurementTwoCh9(NamedTuple):
    '''
    负载箱2-CH9/10
    '''
    slave_address: int = 21


class ResistanceMeasurementTwoCh11(NamedTuple):
    '''
    负载箱2-CH11/12
    '''
    slave_address: int = 22


class ResistanceMeasurementTwoCh13(NamedTuple):
    '''
    负载箱2-CH13/14
    '''
    slave_address: int = 23


class ResistanceMeasurementTwoCh15(NamedTuple):
    '''
    负载箱2-CH15/16
    '''
    slave_address: int = 24


class MicSgCan(NamedTuple):
    '''
    MIC/SG//CAN
    '''
    slave_address: int = 26
    MIC_01: int = 0
    MIC_02: int = 1
    MIC_03: int = 2
    MIC_04: int = 3
    MIC_05: int = 4
    MIC_06: int = 5
    MIC_07: int = 6
    MIC_08: int = 7
    SG_1_01: int = 8
    SG_2_01: int = 9
    SG_2_02: int = 10
    CAN_02: int = 11


if __name__ == '__main__':
    print(DigitalSource)
