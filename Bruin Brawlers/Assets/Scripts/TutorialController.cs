using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Windows.Speech;

public class TutorialController : MonoBehaviour
{
    public TextMeshProUGUI tutInstruction;
    private int tutIndex;
    private KeywordRecognizer keywordRecognizer;
    private Dictionary<string, Action> actions = new Dictionary<string, Action>();
    private string[] instructions = new string[] { "Move Forward!", "Move Backward!", "Throw a Punch!", "Block!", "Kick!", "Throw Your Strongest Punch!"};

    public Image PunchImg;
    public Image BlockImg;
    public Image KickImg;

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
            UpdateImage();
        }
        Debug.Log(instructions.Length);
    }

    private void UpdateImage()
    {
        PunchImg.gameObject.SetActive(false);
        BlockImg.gameObject.SetActive(false);
        KickImg.gameObject.SetActive(false);


        if (tutIndex >= 0 && tutIndex < instructions.Length)
        {
            switch (instructions[tutIndex])
            {
                case "Throw a Punch!":
                    PunchImg.gameObject.SetActive(true);
                    break;
                case "Block!":
                    BlockImg.gameObject.SetActive(true);
                    break;
                case "Kick!":
                    KickImg.gameObject.SetActive(true);
                    break;
            }
        }
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

        PunchImg.gameObject.SetActive(false);
        BlockImg.gameObject.SetActive(false);
        KickImg.gameObject.SetActive(false);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
