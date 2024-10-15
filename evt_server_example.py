import sys

import ccs
from ccs.simpleServer import simpleServer
import rtdcPy

class rtdcEvtTestServer(simpleServer):
    """
    Extends the simple server from CCS and adds the ability to check when a receive event's socket
    file descriptor is updated and then receive the image on each update.
    """
    def __init__(self, cam_name, debug=False):
        """
        Constructor
        """
        # Initialise the server and register with CCS
        super().__init__(f"rtdcEvtTestServer_{cam_name}")

        # Initialise the receive event
        self.recv_evt = rtdcPy.rtdEVT_RECV(cam_name, debug)
        self.recv_evt.Init()
        
        # Initialise the file descriptor to None
        self.fd = None

    def Attach(self):
        """
        Method to attach the RTD event to the camera and add a reader to the asyncio loop to call a
        callback on file descriptor updates.
        """
        # Attach the receive event to the camera
        self.recv_evt.Attach(callback=self._RtdEvtCB)

    def _RtdEvtCB(self):
        """
        Callback function to read the image from the RTD whenever a full rtdPACKET structure is
        written to the socket and print it to stdout.
        """
        try:
            # Receive the image information (actually reads from the socket)
            self.recv_evt.RecvImgInfo()

            # Check that the image is complete
            if not self.recv_evt.IsCompleted():
                print("Event not complete\n")
                return

            # Get the image data and print it to stdout
            data = self.recv_evt.RecvImg()
            print(data)
        except ccs.error as err:
            # Handle errors
            stack, _, _ = err.args
            stack.Close()

    def Close(self):
        """
        Cleans up the receive event
        """
        if self.recv_evt.IsAttached():
            self.recv_evt.Detach()
        self.recv_evt.Close()

    def cbEXIT(self, *args):
        """
        Overrides the default EXIT callback to ensure that the RTD event is properly closed
        """
        self.Close()
        return super.cbEXIT(*args)


# Create an instance of the server object with the camera name passed as the first argument to the
# program
server = rtdcEvtTestServer(sys.argv[1], False)

# Attach the event to the camera and start the server loop
server.Attach()
server.MainLoop()
