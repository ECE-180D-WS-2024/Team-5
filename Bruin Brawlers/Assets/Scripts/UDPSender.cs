using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;

public class UDPSender : MonoBehaviour
{
    public string ipAddress = "127.0.0.1"; // The IP address to send the packet to
    public int port = 6000; // The port to send the packet to

    private UdpClient udpClient;

    void Start()
    {
        Debug.Log(port);
        udpClient = new UdpClient();
    }

    public void SendUDPPacket(string message)
    {
        try
        {
            IPEndPoint endPoint = new IPEndPoint(IPAddress.Parse(ipAddress), port);
            byte[] sendBytes = Encoding.ASCII.GetBytes(message);
            udpClient.Send(sendBytes, sendBytes.Length, endPoint);
            Debug.Log("Packet sent to " + ipAddress + ":" + port);
        }
        catch (System.Exception e)
        {
            Debug.LogError("Error sending UDP packet: " + e.Message);
        }
    }

    void OnDestroy()
    {
        if (udpClient != null)
        {
            udpClient.Close();
        }
    }
}
