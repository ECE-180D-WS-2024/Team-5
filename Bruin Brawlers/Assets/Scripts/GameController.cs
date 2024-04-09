using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameController : MonoBehaviour
{
    public GameOverScreen gameOverScreen;
    public HealthBar p1HB;
    public HealthBar p2HB;

    private void EndGame(string winner)
    {
        //GameObject player1 = GameObject.FindWithTag("Player 1");
        //GameObject player2 = GameObject.FindWithTag("Player 2");

        //p1.GetComponent<PlayerActionScript>().enabled = false;
        //p2.GetComponent<Player2ActionScript>().enabled = false;
        gameOverScreen.Setup(winner);
    }

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (p1HB.GetHealth() == 0)
        {
            EndGame("Player 2");
        }
        
        if (p2HB.GetHealth() == 0)
        {
            EndGame("Player 1");
        }
    }
}
