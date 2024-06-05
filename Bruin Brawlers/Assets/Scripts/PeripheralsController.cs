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
    void Start()
    {
        StartCoroutine(RunPythonCouroutine());
        //await RunPythonScriptAsync();
    }

    // Asynchronous method to run the Python script
    private IEnumerator RunPythonCouroutine()
    {
        // Path to the Python script
        string scriptPath = @"./main.py";

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

        using (gesture_recog = new Process { StartInfo = start })
        {
            gesture_recog.Start();
            Debug.Log("Starting script...");

            // Read the output and error asynchronously
            Task<string> stdoutTask = gesture_recog.StandardOutput.ReadToEndAsync();
            Task<string> stderrTask = gesture_recog.StandardError.ReadToEndAsync();

            yield return new WaitUntil(() => stdoutTask.IsCompleted && stderrTask.IsCompleted);

            string stdout = stdoutTask.Result;
            string stderr = stderrTask.Result;

            if (!string.IsNullOrEmpty(stdout))
            {
                Debug.Log($"Python stdout: {stdout}");
            }

            if (!string.IsNullOrEmpty(stderr))
            {
                Debug.LogError($"Python stderr: {stderr}");
            }
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
