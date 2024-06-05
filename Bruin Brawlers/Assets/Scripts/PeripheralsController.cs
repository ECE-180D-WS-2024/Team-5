using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Diagnostics;
using System.Threading.Tasks;
using Debug = UnityEngine.Debug;
using UnityEditor;

public class PeripheralsController : MonoBehaviour
{
    private Process gesture_recog;
    async void Start()
    {
        await RunPythonScriptAsync();
    }

    // Asynchronous method to run the Python script
    public async Task RunPythonScriptAsync()
    {
        // Path to the Python script
        string scriptPath = @"../Data_Transmission/main.py";

        // Arguments to pass to the script
        string scriptArgs = "";

        // Create a new process
        ProcessStartInfo start = new ProcessStartInfo
        {
            FileName = "python",
            Arguments = $"{scriptPath} {scriptArgs}",
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };

        Debug.Log("Starting script...");
        using (gesture_recog = new Process { StartInfo = start })
        {
            gesture_recog.Start();

            // Read the output (or the error)
            string stdout = await gesture_recog.StandardOutput.ReadToEndAsync();
            string stderr = await gesture_recog.StandardError.ReadToEndAsync();
        }
    }

    // Update is called once per frame
    void Update()
    {
     
    }

    private void OnApplicationQuit()
    {
        gesture_recog.Kill();
    }
}
