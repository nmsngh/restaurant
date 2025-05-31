using UnityEngine;
using IoT;
using System.Xml.Linq;
using System.Threading.Tasks;
using System.IO;
using System.Text;
using System;
using Unity.VisualScripting;
using UnityEngine.UI;
using TMPro;
using UnityEngine.Experimental.GlobalIllumination;
using System.Collections;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Net;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
public class Sensors : MonoBehaviour
{
    public float timeSpan = 5;
    private float time = 0;
    public float temp = 24;
    public float lux = 200;
    public float db = 70;
    public float humid = 20;
    public float syncSpan = 600;
    public Light bulb;
    public Slider tempSlider, dbSlider, luxSlider, humidSlider;
    public TMP_Text tempText, dbText, luxText, humidText, info;
    public GameObject server;

    private void SetInfo(string ip, int r, int g, int b)
    {        
        string text = $"Bulb Color : ({r}, {g}, {b})\nMN HOST : {ip}\nRestaurant Mood tracker Simulator 1.0.0";
        info.text = text;
    }

    public static string GetLocalIPv4()
    {
        string localIP = "";
        try
        {
            NetworkInterface[] interfaces = NetworkInterface.GetAllNetworkInterfaces();
            foreach (NetworkInterface adapter in interfaces)
            {
                if (adapter.OperationalStatus == OperationalStatus.Up &&
                    (adapter.NetworkInterfaceType == NetworkInterfaceType.Wireless80211 ||
                     adapter.NetworkInterfaceType == NetworkInterfaceType.Ethernet))
                {
                    foreach (UnicastIPAddressInformation ip in adapter.GetIPProperties().UnicastAddresses)
                    {
                        if (ip.Address.AddressFamily == AddressFamily.InterNetwork &&
                            !IPAddress.IsLoopback(ip.Address))
                        {
                            localIP = ip.Address.ToString();
                            return localIP;
                        }
                    }
                }
            }
            if (string.IsNullOrEmpty(localIP))
            {
                using (Socket socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, 0))
                {
                    socket.Connect("8.8.8.8", 65530);
                    IPEndPoint endPoint = socket.LocalEndPoint as IPEndPoint;
                    localIP = endPoint.Address.ToString();
                }
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Failed to get local IP: {ex.Message}");
            return "127.0.0.1";
        }

        return localIP;
    }

    public async void Start()
    {
        FileStream fs = new FileStream("config.ini", FileMode.Open, FileAccess.Read);
        StreamReader streamReader = new StreamReader(fs);
        OneM2M.baseUrl = streamReader.ReadLine().Replace(Environment.NewLine, "");
        NotificationServer.port = int.Parse(streamReader.ReadLine().Replace(Environment.NewLine, ""));        
        SetInfo(OneM2M.baseUrl, (int)bulb.GetComponent<Light>().color.r, (int)bulb.GetComponent<Light>().color.g, (int)bulb.GetComponent<Light>().color.b);
        try
        {
            await CreateAE("Sensor", "CSensors");
            await CreateAE("SmartBulb", "CSmartBulb");
            await CreateSubscription("command", $"http://172.19.14.80:{NotificationServer.port}/notifi");
        }
        catch
        {

        }
        StartCoroutine(syncData());

    }

    public static string EscapeJsonString(string rawString)
    {
        if (string.IsNullOrEmpty(rawString))
            return rawString;

        return rawString
            .Replace("\\", "\\\\")  // �齽����
            .Replace("\"", "\\\"")  // ����ǥ
            .Replace("\b", "\\b")   // �齺���̽�
            .Replace("\f", "\\f")   // �� �ǵ�
            .Replace("\n", "\\n")   // �ٹٲ�
            .Replace("\r", "\\r")   // ĳ���� ����
            .Replace("\t", "\\t");  // ��
    }

    public async void Update()
    {
        SetInfo(OneM2M.baseUrl, (int)(bulb.GetComponent<Light>().color.r * 255), (int)(bulb.GetComponent<Light>().color.g * 255), (int)(bulb.GetComponent<Light>().color.b * 255));
        if (OneM2M.checkCommand)
        {
            OneM2M.checkCommand = false;
            Debug.Log("Check command");
            string result = await OneM2M.GetDataAsync("CSmartBulb", "osori", "SmartBulb/command/la");
            //result = result.Replace("\\", "");
            Debug.Log(result);
            JObject json = JObject.Parse(result);
            json = JObject.Parse(json["m2m:cin"]["con"].ToString());
            luxSlider.value = float.Parse(json["lux"].ToString());
            float r = float.Parse(json["r"].ToString()) / 255f;
            float g = float.Parse(json["g"].ToString()) / 255f;
            float b = float.Parse(json["b"].ToString()) / 255f;
            bulb.GetComponent<Light>().color = new Color(r, g, b);
        }
        temp = (float)Math.Round(tempSlider.value, 1);
        db = (float)Math.Round(dbSlider.value, 1);
        lux = (float)Math.Round(luxSlider.value, 1);
        humid = (float)Math.Round(humidSlider.value, 1);        
        tempText.text = temp.ToString() + " ��C";
        dbText.text = db.ToString() + " db";
        luxText.text = lux.ToString() + " lux";
        humidText.text = humid.ToString() + " %";
        bulb.intensity = lux / 100;
        time += Time.deltaTime;        
    }
    IEnumerator syncData()
    {
        float timeSpan = 7.0f;

        while (true)
        {
            CreateContentInstance("temperature", $"{{\"temp\":{temp}}}");
            CreateContentInstance("noise", $"{{\"noise\":{db}}}");
            CreateContentInstance("humid", $"{{\"humidity\":{humid}}}");
            yield return new WaitForSeconds(timeSpan);
        }
    }
    public async Task<string> CreateAE(string name, string origin)
    {
        Debug.Log("Create " + name);
        string requestBody = @"{
            ""m2m:ae"": {
                ""rn"": """ + name + @""",
                ""api"": ""N_Sensor_AE"",
                ""rr"": true,
                ""srv"": [""3""]
            }
        }";
        string res = await OneM2M.PostDataAsync(origin, 2, requestBody, "osori");
        return res;
    }
    public async Task<string> CreateContentInstance(string containerName, string content)
    {
        string requestBody = @"{
            ""m2m:cin"": {
                ""con"": """ + EscapeJsonString(content) + @"""
            }
        }";
        Debug.Log(requestBody);
        string res = await OneM2M.PostDataAsync("CSensors", 4, requestBody, "osori", "Sensors/" + containerName);
        return res;
    }
    public async Task<string> CreateSubscription(string containerName, string notificationUrl)
    {
        string requestBody = @"{
        ""m2m:sub"": {
            ""rn"": ""SUB_" + containerName + @""",
            ""enc"": {
                ""net"": [3]
            },
            ""nu"": [""" + notificationUrl + @"""],
            ""nct"": 1
        }
    }";
        Debug.Log(requestBody);
        string res = await OneM2M.PostDataAsync("CSmartBulb", 23, requestBody, "osori", "SmartBulb/" + containerName);
        return res;
    }

}