class preGame():
    def __init__(self, host, num, title):
        self.host = host
        self.player2 = None
        self.player3 = None
        self.player4 = None

        self.chat = []
        self.chatO = []

        self.chatLimit = 5

        self.num = num
        self.title = title
    def leave(self, pid):
        if self.host == pid:
            ret = []
            if self.player2 != None:
                ret.append(self.player2)
            if self.player3 != None:
                ret.append(self.player3)
            if self.player4 != None:
                ret.append(self.player4)
            return ret
        else:
            return False
