using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MenuController : MonoBehaviour
{
    public void PlayButton()
    {
        Debug.Log("CLICK");
        SceneManager.LoadScene("Scenes/Tutorial");
    }

    public void QuitButton()
    {
        Application.Quit();
    }
}
