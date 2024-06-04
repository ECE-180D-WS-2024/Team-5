using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System;
using System.Diagnostics;

public class PeripheralsController : MonoBehaviour
{
    // Start is called before the first frame update
    void Start()
    {
        // Path to the Python script
        string scriptPath = @"../../../Gesture Recognition/mediapipe_height_relative.py";

        // Arguments to pass to the script
        string scriptArgs = "";

        // Create a new process
        ProcessStartInfo start = new ProcessStartInfo();
        start.FileName = "python";
        start.Arguments = $"{scriptPath} {scriptArgs}";
        start.UseShellExecute = false;
        start.RedirectStandardOutput = true;
        start.RedirectStandardError = true;
        start.CreateNoWindow = true;

        using (Process process = Process.Start(start))
        {
            // Read the output (or the error)
            string stdout = process.StandardOutput.ReadToEnd();
            string stderr = process.StandardError.ReadToEnd();

            process.WaitForExit();

            Console.WriteLine("Output:");
            Console.WriteLine(stdout);
            Console.WriteLine("Errors:");
            Console.WriteLine(stderr);
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
