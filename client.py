import socket
from blockdef import BlockDef
import json
target_ip = "ec2-54-248-128-220.ap-northeast-1.compute.amazonaws.com"
target_port = 1234
buffer_size = 8192



def readblock(definition):
    x=[]
    for i in range(len(definition)):
        x.append(i)
    return x

class gameLogic:
    def __init__(self):
        self.field=[[0]*20 for i in range(20)]
        self.KndBlock=BlockDef.definition
        self.myblocks=readblock(self.KndBlock)
        self.turn=0
        self.Blockw=5
        self.Blockh=5
        self.Fieldw=20
        self.Fieldh=20

    def changeTurn(self):
        self.turn=(self.turn+1)%4
        cnt=0
        while not self.earyput(True):
            self.turn=(self.turn+1)%4
            cnt+=1
            if cnt==4:exit()


    def isIn(self,x,y):
        if x<0 or y<0 or self.Fieldw<=x or self.Fieldh<=y:return False
        return True

    def canPut(self,x,y,spin,blockId,color):
        edge=False
        Blockw=self.Blockw
        Blockh=self.Blockh

        Fieldw=self.Fieldw
        Fieldh=self.Fieldh
        side=[[1,0],[0,1],[-1,0],[0,-1]]
        cross=[[1,1],[-1,-1],[-1,1],[1,-1]]
        targetBlock = self.KndBlock[blockId][spin]
        for i in range(25):
            if not targetBlock[i]:continue
            if not self.isIn(x+i%Blockw,y+i//Blockw):return False
            if self.field[y+i//Blockw][x+i%Blockw]!=0:return False
            if (x+i%Blockw==0 or x+i%Blockw==Fieldw-1) and (y+i//Blockw==0 or y+i//Blockw==Fieldh-1):edge=True
            for j in range(4):
                if not self.isIn(x+i%Blockw+side[j][0],y+i//Blockw+side[j][1]):continue
                if self.field[y+i//Blockw+side[j][1]][x+i%Blockw+side[j][0]]==color:return False
            for j in range(4):
                if not self.isIn(x+i%Blockw+cross[j][0],y+i//Blockw+cross[j][1]):continue
                if self.field[y+i//Blockw+cross[j][1]][x+i%Blockw+cross[j][0]]==color:edge=True
        return edge
    def putBlock(self,x,y,spin,blockId,color):
        Blockw=self.Blockw
        Blockh=self.Blockh

        Fieldw=self.Fieldw
        Fieldh=self.Fieldh
        if not self.canPut(x,y,spin,blockId,color):return False
        targetBlock = self.KndBlock[blockId][spin]
        for i in range(25):
            if not targetBlock[i]:continue
            self.field[y+i//Blockw][x+i%Blockw]=color
        
        if self.turn==self.myColor:
            self.myblocks.remove(blockId)
        self.changeTurn()
        return True

    def easyDisp(self):
        for i in self.field:
            print(*i)

    def Test(self,color):
        for num in range(4):
            for i in range(900):
                print(self.putBlock(-3+i//30,-3+i%30,0,0,color+1),i)
    def receiveInit(self,message):
        jsondic=json.loads(message)
        s=jsondic["PlayerRotation"].split(",")
        for i,color in enumerate(s):
            if jsondic["yourColor"]==color:
                self.myColor=i
                break
        print("init success myturn is ",self.myColor)
        if self.turn==self.myColor:
            self.earyput(False)
    def earyput(self,isCheckMode):
        for num in self.myblocks:
            for i in range(900):
                for spin in range(4):
                    if self.canPut(-3+i%30,-3+i//30,spin,num,self.turn+1):
                        if isCheckMode:return True
                        data={}
                        data["x"]=-3+i%30
                        data["y"]=-3+i//30
                        data["spin"]=spin
                        data["BlockId"]=num
                        data["color"]=self.turn 
                        print(json.dumps(data))
                        self.client.send(json.dumps(data).encode())
                        return

        print("pass!!")
        return False

    def getCanPutList(self):
        ans=[]
        for num in self.myblocks:
            for i in range(900):
                for spin in range(4):
                    if self.canPut(-3+i%30,-3+i//30,spin,num,self.turn+1):
                        ans.append([num,spin,-3+i%30,-3+i//30])
        return ans
    def randomizeField(self):
        import random
        for i in range(20):
            for j in range(20):
                self.field[i][j]=random.randint(0,4)&random.randint(0,4)

    def receiveUpdate(self,message):
        jsondic=json.loads(message)
        s=jsondic["Blocks"].split(',')
        color=int(s[-5])
        x=int(s[-4])
        y=int(s[-3])
        blockId=int(s[-2])
        spin=int(s[-1])
        print(self.putBlock(x,y,spin,blockId,color+1))
        self.easyDisp()
        print(x,y,blockId,spin,color)
        if self.turn==self.myColor:
            self.earyput(False)
        
    def receiveMessage(self,message):
        print(message)
        jsondic=json.loads(message)
        if jsondic["messageType"]=="Init":self.receiveInit(message)
        if jsondic["messageType"]=="Update":self.receiveUpdate(message)

    def setclient(self,client):
        self.client=client


game=gameLogic()
game.easyDisp()

game.randomizeField()
game.easyDisp()
print(game.getCanPutList())

exit(0)




# 1.ソケットオブジェクトの作成
tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.サーバに接続
tcp_client.connect((target_ip,target_port))

# サーバにデータを送信
#tcp_client.send(b"Data by TCP Client!!")
game.setclient(tcp_client)

s=""
while True:
  # サーバからのレスポンスを受信
  response = tcp_client.recv(buffer_size)
  s+=response.decode()
  if response.decode()[-1]!="\n":
    continue
  print(s)
  game.receiveMessage(s)
  print("[*]Received a response : {}".format(response))
  s=""
