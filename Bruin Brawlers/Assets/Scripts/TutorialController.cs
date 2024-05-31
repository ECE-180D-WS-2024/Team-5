using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Windows.Speech;

public class TutorialController : MonoBehaviour
{
    public TextMeshProUGUI tutInstruction;
    private int tutIndex;
    private KeywordRecognizer keywordRecognizer;
    private Dictionary<string, Action> actions = new Dictionary<string, Action>();
    private string[] instructions = new string[] { "Move Forward!", "Move Backward!", "Throw a Punch!", "Block!", "Kick!", "Throw Your Strongest Punch!"};

    private void RecognizedSpeech(PhraseRecognizedEventArgs speech)
    {
        Debug.Log(speech.text);
        actions[speech.text].Invoke();
    }

    private void getNextInstruction()
    {
        tutIndex++;
        if (tutIndex < instructions.Length - 1)
        {
            tutInstruction.text = instructions[tutIndex];
        }
        Debug.Log(instructions.Length);
    }

    // Start is called before the first frame update
    void Start()
    {
        tutInstruction.text = "Tutorial";
        tutIndex = -1;
        actions.Add("Continue", () => getNextInstruction());

        keywordRecognizer = new KeywordRecognizer(actions.Keys.ToArray());
        keywordRecognizer.OnPhraseRecognized += RecognizedSpeech;
        keywordRecognizer.Start();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
