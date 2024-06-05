using System;
using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
public class UDPReciever : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 5000; // Select a port to listen on
    public static String p1Move;
    public static String p2Move;
    public static String p1Action = "";
    public static String p2Action = "";

    public static UDPReciever Instance { get; private set; }

    void Awake()
    {
        if (Instance == null)
        {
            Instance = this;
            DontDestroyOnLoad(gameObject);
        }
        else
        {
            Destroy(gameObject);
        }
    }
    private void StartReceiving()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
        Debug.Log("Connected to port 5000!");
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (true)
        {
            try
            {
                // Blocks until a message returns on this socket from a remote host.
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);

                string text = Encoding.UTF8.GetString(data);
                if (text.Contains("p1-Move"))
                {
                    UDPReciever.p1Move = text;
                    Debug.Log(UDPReciever.p1Move);
                }
                else if (text.Contains("p2-Move"))
                {
                    UDPReciever.p2Move = text;
                    Debug.Log(UDPReciever.p2Move);
                }
                else if (text.Contains("p1"))
                {
                    UDPReciever.p1Action = text;
                    Debug.Log(UDPReciever.p1Action);
                }
                else if (text.Contains("p2"))
                {
                    UDPReciever.p2Action = text;
                    Debug.Log(UDPReciever.p2Action);
                }
                // Process the data received (e.g., by parsing text) here
            }
            catch (Exception e)
            {
                Debug.LogError(e.ToString());
            }
        }
    }

    public void SendUDPPacket(string message, int endPort)
    {
        try
        {
            IPEndPoint endPoint = new IPEndPoint(IPAddress.Parse("127.0.0.1"), endPort);
            byte[] sendBytes = Encoding.ASCII.GetBytes(message);
            client.Send(sendBytes, sendBytes.Length, endPoint);
            Debug.Log("Packet sent to " + "127.0.0.1" + ":" + endPort);
        }
        catch (System.Exception e)
        {
            Debug.LogError("Error sending UDP packet: " + e.Message);
        }
    }

    void Start()
    {
        StartReceiving();
    }

    private void closeSocket()
    {
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Abort();
        }

        if (client != null)
        {
            client.Close();
        }
    }

    void OnApplicationQuit()
    {
        closeSocket();
    }

    private void OnDestroy()
    {
        closeSocket();
    }
}