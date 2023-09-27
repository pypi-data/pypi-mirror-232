
from Anapass.TModule import *

def Test_RREG1(device) :
    
    regAddr=1307
    readCount=5  # 5바이트 
    regValueList = device.RREG1(regAddr, readCount)  #레지스터 Read함수 
    if regValueList == None :
        print("FAIL: ReadReg,  Check the connection between TMonitor and T4/T5 Device")
        quit()
    
    # ChipID 읽은 결과 출력
    print("RREG1 = %d, " % regAddr, end='')    
    for regValue in regValueList :
        print(hex(regValue), end=',')
    print("")

def Test_WREG1(device) :
    regAddr=1307
    regValueList=[0xAA, 0xBB, 0xCC, 0xDD, 0xEE]
    isOK = device.WREG1(regAddr, regValueList)
    if isOK != True :
        print("FAIL: WREG1,  Check the connection between TMonitor and T4/T5 Device")
        quit()
    print("WREG1 = %d, " % regAddr, end='')    
    for regValue in regValueList :
        print(hex(regValue), end=',')
    print("")

if __name__ == "__main__" :
    
    #
    #  T5에 연결후,  ChipID를 읽고, 화면에 출력하는 예제 
    #
    print("----------------------------------------------")
    print("[anapass-python::Example] Test RREG1, RREG1 ")
    print("----------------------------------------------")

    #TDevice 객체 생성, T5연결하는 Device객체이다.
    device = TDevice(TDevice.Type.T5)

    # Python프로그램을 Device를  연결하는 코드이다.
    # T4/T5 에 연결해서 사용하기 위해서는, 먼저  TEDTools의 TMonitor가 활성화되어야 한다. 
    # http://aits.anapass.com:8090/display/SI/TED+Tools  에서 UserManual Chap2. 'T4/T5구동기 연결하기' 참고 
    print("Connect To " + device.GetName())
    isConnect = device.Connect()
    if isConnect != True :
        print("Connect Fail")
        quit()

    Test_WREG1(device)
    Test_RREG1(device)

    #연결을 끊는다.     
    print("Disconnect from " + device.GetName() )
    device.Disonnect()

    print("End of Exam. Bye!!")
    print()



