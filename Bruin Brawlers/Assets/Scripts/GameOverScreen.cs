using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.SceneManagement;

public class GameOverScreen : MonoBehaviour
{
    public TextMeshProUGUI winText;
    public GameObject mainMenuBackground;
    public void Setup(string winner)
    {
        gameObject.SetActive(true);
        winText.text = winner + " WINS!";
    }

    public void Pause()
    {
        if (gameObject.activeSelf)
        {
            gameObject.SetActive(false);
        }
        else
        {
            gameObject.SetActive(true);
            winText.text = "PAUSE (ESC to Resume)";
        }
    }

    public void RestartButton()
    {
        SceneManager.LoadScene("Game");
    }

    public void MainMenuButton()
    {
        SceneManager.LoadScene("Main Menu");
    }
}
