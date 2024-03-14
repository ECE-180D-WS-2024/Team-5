using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Xml.Serialization;
using UnityEngine;
using UnityEngine.Windows.Speech;
using UnityEngine.Networking;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class Player2ActionScript : MonoBehaviour
{
    Thread receiveThread;
    UdpClient client;
    public int port = 5000; // Select a port to listen on

    public Rigidbody2D myRigidBody;
    public BoxCollider2D myCollider;
    public BoxCollider2D enemyCollider;
    public Animator animator;
    public string lastMove;
    public int maxHP = 100;
    public int currentHP;
    public HealthBar enemyHealthBar;
    public HealthBar healthBar;
    public String move;

    private KeywordRecognizer keywordRecognizer;
    private Dictionary<string, Action> actions = new Dictionary<string, Action>();
    private Vector3 originalScale;
    private Color originalColor;
    private bool activeSM = false;
    private bool cooldownSM = false;

    // Start is called before the first frame update
    void Start()
    {
        StartReceiving();

        lastMove = "";
        currentHP = maxHP;
        healthBar.SetMaxHealth(maxHP);

        actions.Add("fergalicious", () => superMove());

        keywordRecognizer = new KeywordRecognizer(actions.Keys.ToArray());
        keywordRecognizer.OnPhraseRecognized += RecognizedSpeech;
        keywordRecognizer.Start();

        originalScale = myRigidBody.transform.localScale;
        originalColor = GetComponent<SpriteRenderer>().color;
    }

    private void StartReceiving()
    {
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    private void ReceiveData()
    {
        client = new UdpClient(port);
        while (true)
        {
            try
            {
                // Blocks until a message returns on this socket from a remote host.
                IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, 0);
                byte[] data = client.Receive(ref anyIP);

                string text = Encoding.UTF8.GetString(data);
                move = text;
                Debug.Log(">> " + text);

                // Process the data received (e.g., by parsing text) here
            }
            catch (Exception e)
            {
                Debug.LogError(e.ToString());
            }
        }
    }

    void OnApplicationQuit()
    {
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Abort();
        }

        if (client != null)
        {
            client.Close();
        }
    }
    private void RecognizedSpeech(PhraseRecognizedEventArgs speech)
    {
        Debug.Log(speech.text);
        actions[speech.text].Invoke();
    }

    // Update is called once per frame
    void Update()
    {
        if (enemyCollider.IsTouching(myCollider))
        {
            animator.SetTrigger("isHurt");
        }

        if (Input.GetKeyDown(KeyCode.UpArrow) && lastMove != "JUMP")
        {
            Debug.Log("JUMP");
            animator.SetTrigger("isJumping");
            myRigidBody.velocity = Vector2.up * 5;
            lastMove = "JUMP";
        }
        if (Input.GetKeyDown(KeyCode.LeftArrow))
        {
            //animator.SetBool("isMoving", true);
            myRigidBody.velocity = Vector2.left * 15;
            animator.SetBool("isMoving", true);
        }
        if (Input.GetKeyDown(KeyCode.DownArrow))
        {
            myRigidBody.velocity = Vector2.down * 15;
            //animator.SetBool("isMoving", true);
        }
        if (Input.GetKeyDown(KeyCode.RightArrow))
        {
            //animator.SetBool("isMoving", true);
            myRigidBody.velocity = Vector2.right * 15;
            //animator.SetBool("isMoving", true);
            StartCoroutine(runAnimation("isMoving", 2f));
        }
        if (move == "Punch")
        {
            Debug.Log("PUNCH!");
            animator.SetTrigger("isPunching");
            if (myCollider.IsTouching(enemyCollider))
            {
                Debug.Log("Hit ENEMY!");
                int enemyHP = enemyHealthBar.GetHealth() - 4;
                enemyHealthBar.SetHealth(enemyHP);
            }
        }
        if (Input.GetKeyDown(KeyCode.K))
        {
            Debug.Log("KICK!");
        }
        if (Input.GetKeyDown(KeyCode.L))
        {
            Debug.Log("BLOCK!");
        }
        if (activeSM)
        {
            StartCoroutine(SuperMoveCoroutine());
            activeSM = false;
        }
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.tag == "Ground")
        {
            lastMove = "";
        }
    }

    void OnTriggerEnter2D(Collider2D target)
    {
        if (target.tag == "Player")
        {
            Debug.Log("Hit ENEMY!!!");
        }

    }

    private IEnumerator runAnimation(string animation, float time)
    {
        // Set the boolean to true to indicate the transition is in progress
        animator.SetBool(animation, true);

        // Call your transition method here (e.g., using Unity's UI or animation system)
        // Replace the WaitForSeconds duration with the actual duration of your transition
        yield return new WaitForSeconds(time); // Adjust this duration as needed

        // Reset the boolean after the transition is complete
        animator.SetBool(animation, false);
    }

    private void superMove()
    {
        if (!cooldownSM)
        {
            activeSM = true;
            cooldownSM = true;
        }
    }

    private IEnumerator SuperMoveCoroutine()
    {
        myRigidBody.transform.localScale += new Vector3(1f, 1f, 1f);
        GetComponent<SpriteRenderer>().color = new Color(0, 1, 0, 1);

        yield return new WaitForSeconds(10f);   //wait for 10 seconds

        myRigidBody.transform.localScale = originalScale;
        GetComponent<SpriteRenderer>().color = originalColor;

        cooldownSM = false;
    }
}
