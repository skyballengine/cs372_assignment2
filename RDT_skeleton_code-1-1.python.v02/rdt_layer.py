from segment import Segment
from unreliable import UnreliableChannel


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    # Add items as needed\
    name = None
    currentSeqnum = 0
    currentAcknum = 0
    unreceivedAcknum = 0
    unAckedIteration = 0
    buffer = ''
    receivedData = ''
    bufferDict = {}
    serverUnAckedSegList = []
    MAX_ITERATIONS = 3
    cumulativeAckNum = 0
    countSegmentTimeouts = 0

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self, name):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed
        self.name = name
        self.currentSeqnum = 0
        self.currentAcknum = 0
        self.unreceivedAcknum = 0
        self.unAckedIteration = 0
        self.buffer = ''
        self.receivedData = ''
        self.bufferDict = {}
        self.serverUnAckedSegList = []
        self.MAX_ITERATIONS = 3
        self.cumulativeAckNum = 0
        self.countSegmentTimeouts = 0


    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self, data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...

        # print('getDataReceived(): Complete this...')
        # print(self.bufferDict)
        keys = list(self.bufferDict.keys())
        keys.sort()
        sorted_list = [self.bufferDict[j] for j in keys]
        self.receivedData = "".join(sorted_list)
         
        # ############################################################################################################ #
        return self.receivedData

        # ############################################################################################################ #
        # return self.buffer

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):
        # segmentSend = Segment()

        # ############################################################################################################ #
        # print('processSend(): Complete this...')

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)

        # client
        if self.name == "client":
            seqnum = self.currentSeqnum
            segnum = 0

            while (segnum < self.FLOW_CONTROL_WIN_SIZE//self.DATA_LENGTH):
                data = ''
                if (seqnum == len(self.dataToSend)):
                    break
                if (len(self.dataToSend) - len(self.buffer)) < self.DATA_LENGTH:
                    num_remaining_chars = len(self.dataToSend) - len(self.buffer)
                    data += self.dataToSend[seqnum: seqnum + num_remaining_chars]
                    seqnum += num_remaining_chars
                    segnum = self.FLOW_CONTROL_WIN_SIZE//self.DATA_LENGTH
                else:
                    data += self.dataToSend[seqnum: seqnum + self.DATA_LENGTH]
                    seqnum += self.DATA_LENGTH
                    segnum += 1

                # Display sending segment - send one at a time with currentSeqnum
                segmentSend = Segment()
                segmentSend.setData(self.currentSeqnum, data)
                # increment currentSeqnum by 4
                self.currentSeqnum = seqnum
                print("Sending segment: ", segmentSend.to_string())

                # Use the unreliable sendChannel to send the segment
                self.sendChannel.send(segmentSend)
                    

        # server
        else:
            # print("Server bypassing processSend()because NO data to send.....")
            pass


    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        segmentAck = Segment()                  # Segment acknowledging packet(s) received

        # This call returns a list of incoming segments (see Segment class)...
        listIncomingSegments = self.receiveChannel.receive()

        # ############################################################################################################ #
        # What segments have been received?
        # How will you get them back in order?
        # This is where a majority of your logic will be implemented
        # print('processReceive(): Complete this...')
        acknum = -1

        # client
        if self.name == "client":
            acknum = 1
            if listIncomingSegments:
                response = listIncomingSegments[0]
                if self.currentSeqnum != response.acknum:
                    self.countSegmentTimeouts += 1
                self.currentSeqnum = response.acknum
            acknum = 1

        
        # server
        else:
            acknum = self.currentAcknum
            for segment in listIncomingSegments:
                if segment.payload:
                    # print(f"Segment from client:{segment.to_string()} ")
                    # check checksum
                    if segment.checkChecksum():
                        self.bufferDict[segment.seqnum] = segment.payload

                        # check if seqnum is in the unAcked list - if so, remove it
                        if segment.seqnum in self.serverUnAckedSegList:
                            # print(f"Removing segment: {segment.seqnum}")
                            self.serverUnAckedSegList.remove(segment.seqnum)
                            # print(f"UnAcked segment list: {self.serverUnAckedSegList}")

                    # ############################################################################################################ #
                    # How do you respond to what you have received?
                    # How can you tell data segments apart from ack segemnts?
                    # print('processReceive(): Complete this...')

                    # Somewhere in here you will be setting the contents of the ack segments to send.
                    # The goal is to employ cumulative ack, just like TCP does...

                    if (segment.seqnum != self.cumulativeAckNum) or (not segment.checkChecksum()):
                        acknum = self.currentAcknum
                        # self.unreceivedAcknum = self.cumulativeAckNum
                        if segment.seqnum not in self.serverUnAckedSegList:
                            # print(f"Adding segment: {segment.seqnum}")
                            self.serverUnAckedSegList.append(segment.seqnum)  
                        # self.currentIteration += 1
                        self.unAckedIteration += 1

                        # selective retransmit - ack for lost packets after 3 iterations
                        if self.unAckedIteration == self.MAX_ITERATIONS:
                            acknum = self.serverUnAckedSegList[0]
                            self.unAckedIteration = 0

                    # expected sequence number - increment cumulativeAckNum
                    else:
                        self.cumulativeAckNum += len(segment.payload)
                        self.currentAcknum = self.cumulativeAckNum
                        acknum = self.cumulativeAckNum
                        if segment.seqnum in self.serverUnAckedSegList:
                            self.serverUnAckedSegList.remove(segment.seqnum)
                else:
                    acknum = self.currentAcknum

        # ############################################################################################################ #
        # Display response segment
        segmentAck.setAck(acknum)
        print("Sending ack: ", segmentAck.to_string())

        # Use the unreliable sendChannel to send the ack packet
        self.sendChannel.send(segmentAck)

