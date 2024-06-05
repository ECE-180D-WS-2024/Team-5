using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using TMPro;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;
using UnityEngine.Windows.Speech;

public class TutorialController : MonoBehaviour
{
    public TextMeshProUGUI tutInstruction;
    public bool calibrationMode;
    public UDPSender UDPSender;

    private int tutIndex;
    private KeywordRecognizer keywordRecognizer;
    private Dictionary<string, Action> actions = new Dictionary<string, Action>();
    private string[] instructions = new string[] { "In Bruin Brawlers you control a kickboxer with the goal of defeating your ultimate rival in this final match! When your HP bar reaches 0 you lose!",
        "You also have a special move meter that charges as you land attacks! Once it fully charges you can unleash your special move to gain extra damage on attacks!",
        "Before we begin we need to calibrate player movement!",
        "Calibration: Let's begin by having Player 1 move to the forward threshold and say NEXT!",
        "Calibrating forward Player 1...",
        "Calibration: Let's begin by having Player 2 move to the forward threshold and say NEXT!",
        "Calibrating forward Player 2...",
        "Calibration: Next Player 1 move to the backward threshold! and say NEXT",
        "Calibrating backward Player 1...",
        "Calibration: Next Player 2 move to the backward threshold and say NEXT!",
        "Calibrating backward Player 2...",
        "Calibration Completed! Let's Begin the tutorial!",
        "Tutorial: Try to move your player forward by taking a step!", "Tutorial: Try to still your player by staying in the idle zone", 
        "Tutorial: Try to move your player backward by taking a step backward!",
        "Tutorial: Throw a Punch!", "Tutorial: Block!", "Tutorial: Kick!", "Tutorial: Throw your strongest punch to activate your players FIRE FIST!",
        "Once players have fully charged their SM Bar by dealing damage they can activate their SUPER MOVE!", "Player 1 can activate their super by shouting BOMBASTIC & Player 2 can activate their super by shouting FERGALICIOUS",
        "Tip: During the main game, Player 1 can pause the game by saying 'Pause' and Player 2 can puase the game by saying 'Wait'",
        "Say Ready to Start Game!"};

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
        if (tutIndex < instructions.Length)
        {
            tutInstruction.text = instructions[tutIndex];
            UpdateImage();
        }
    }

    private void endTutorial()
    {
        SceneManager.LoadScene("Scenes/Game");
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
                case "Calibrating forward Player 1...":
                    UDPSender.SendUDPPacket("P2-ForwardThreshold");
                    break;
                case "Calibrating forward Player 2...":
                    UDPSender.SendUDPPacket("P2-BackwardThreshold");
                    break;
                case "Calibrating backward Player 1...":
                    UDPSender.SendUDPPacket("P2-BackwardThreshold");
                    break;
                case "Calibrating backward Player 2...":
                    UDPSender.SendUDPPacket("P2-BackwardThreshold");
                    break;
                case "Tutorial: Throw a Punch!":
                    PunchImg.gameObject.SetActive(true);
                    break;
                case "Tutorial: Block!":
                    BlockImg.gameObject.SetActive(true);
                    break;
                case "Tutorial: Kick!":
                    KickImg.gameObject.SetActive(true);
                    break;
                default:
                    break;
            }
        }
    }

    // Start is called before the first frame update
    void Start()
    {
        tutInstruction.text = "Welcome to Bruin Brawlers! In this tutorial we have disabled the health bars so we can focus on teaching you the game fundamentals!";
        tutIndex = -1;
        actions.Add("Continue", () => getNextInstruction());
        actions.Add("Ready", () => endTutorial());
        
        keywordRecognizer = new KeywordRecognizer(actions.Keys.ToArray());
        keywordRecognizer.OnPhraseRecognized += RecognizedSpeech;
        keywordRecognizer.Start();

        calibrationMode = true;

        PunchImg.gameObject.SetActive(false);
        BlockImg.gameObject.SetActive(false);
        KickImg.gameObject.SetActive(false);
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.N))
        {
            getNextInstruction();
        }   
    }
}
