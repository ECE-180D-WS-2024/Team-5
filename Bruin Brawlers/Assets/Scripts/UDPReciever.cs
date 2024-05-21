using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Windows.Speech;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using static Unity.Collections.AllocatorManager;
using Unity.Burst.Intrinsics;
using Unity.Mathematics;
public class UDPReciever : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 5000; // Select a port to listen on
    public String p1Move;
    public String p2Move;

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
                if (text.Contains("p1"))
                {
                    p1Move = text;
                }
                else if (text.Contains("p2"))
                {
                    p2Move = text;
                }
                // Process the data received (e.g., by parsing text) here
            }
            catch (Exception e)
            {
                Debug.LogError(e.ToString());
            }
        }
    }

    void Start()
    {
        StartReceiving();
    }

    void OnApplicationQuit()
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
}