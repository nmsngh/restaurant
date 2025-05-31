using UnityEngine;
using System;
using System.Net;
using System.Text;
using System.Threading;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using IoT;

public class NotificationServer : MonoBehaviour
{
    private HttpListener listener;
    private Thread listenerThread;
    public bool isRunning = false;
    private string url;
    public static int port = 6000;

    void OnDestroy()
    {
        StopServer();
    }

    private void Start()
    {
        StartServer();
    }

    public void StartServer()
    {
        try
        {            
            listener = new HttpListener();
            url = $"http://+:{port}/";
            listener.Prefixes.Add(url);
            isRunning = true;
            listener.Start();            
            listenerThread = new Thread(ListenerThread);
            listenerThread.Start();

            Debug.Log($"Server started on port {port}");
        }
        catch (Exception e)
        {
            Debug.LogError($"Failed to start server: {e.Message}");
        }
    }

    private void ListenerThread()
    {
        while (isRunning)
        {

            try
            {                
                var context = listener.GetContext();
                ThreadPool.QueueUserWorkItem(ProcessRequest, context);
            }
            catch (Exception e)
            {
                if (isRunning)
                {
                    Debug.LogError($"Listener error: {e.Message}");
                }
            }
        }
    }

    private void ProcessRequest(object state)
    {
        var context = (HttpListenerContext)state;
        try
        {            
            if (context.Request.HttpMethod == "POST" && context.Request.Url.PathAndQuery == "/notifi")
            {
                // Read request body
                string requestBody;
                using (var reader = new System.IO.StreamReader(context.Request.InputStream, context.Request.ContentEncoding))
                {
                    requestBody = reader.ReadToEnd();
                }

                // Parse JSON
                JObject notification = JsonConvert.DeserializeObject<JObject>(requestBody);
                Debug.Log($"Notification received: {JsonConvert.SerializeObject(notification, Formatting.Indented)}");

                // Check for verification request
                bool isVerification = false;
                if (notification["m2m:sgn"] != null)
                {
                    var sgn = notification["m2m:sgn"];
                    if (sgn["vrq"] != null)
                    {
                        isVerification = sgn["vrq"].Value<bool>();
                    }
                }

                // Create response headers
                context.Response.Headers.Add("X-M2M-RSC", "2000");
                context.Response.Headers.Add("X-M2M-RI", context.Request.Headers["X-M2M-RI"]);
                context.Response.Headers.Add("X-M2M-Origin", "mn-ae");
                context.Response.Headers.Add("X-M2M-RVI", DateTime.UtcNow.ToString("yyyyMMddTHHmmss"));

                // Send response
                context.Response.StatusCode = 200;
                context.Response.Close();

                if (isVerification)
                {
                    Debug.Log("Verification request received");
                }
                else
                    OneM2M.checkCommand = true;
            }
        }
        catch (Exception ex)
        {
            Debug.LogError($"Error processing request: {ex.Message}\nStackTrace: {ex.StackTrace}");
            context.Response.StatusCode = 500;
            context.Response.Close();
        }
    }

    public void StopServer()
    {
        isRunning = false;
        if (listener != null)
        {
            listener.Stop();
            listener.Close();
        }

        if (listenerThread != null)
        {
            listenerThread.Join();
        }

        Debug.Log("Server stopped");
    }

    public void SetPort(int newPort)
    {
        if (isRunning)
        {
            StopServer();
            port = newPort;
            StartServer();
        }
        else
        {
            port = newPort;
        }
    }
}