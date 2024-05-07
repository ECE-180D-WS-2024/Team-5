using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Windows.Speech;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class PlayerActionScript : MonoBehaviour
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
    public int prevHP;
    public HealthBar enemyHealthBar;
    public HealthBar healthBar;
    public int maxSM = 100;
    public int currentSM;
    public SMBar sm_bar;
    public int count = 0;
    public int mySM = 0;
    public String move;
    public bool isDead;
    public bool combo;
    public bool block;
    public Player2ActionScript player2;
    public AudioManager sfxSounds;

    private KeywordRecognizer keywordRecognizer;
    private Dictionary<string, Action> actions = new Dictionary<string, Action>();
    private Vector3 originalScale;
    private Color originalColor;
    private bool activeSM = false;
    private bool cooldownSM = false;
    private bool sm_bar_full = false;

    // Start is called before the first frame update
    void Start()
    {
        StartReceiving();

        lastMove = "";

        combo = false;
        block = false;
        currentHP = maxHP;
        healthBar.SetMaxHealth(maxHP);
        prevHP = healthBar.GetHealth();
        currentSM = 0;
        sm_bar.SetStartSM(0);
        sfxSounds = GameObject.FindGameObjectWithTag("Audio").GetComponent<AudioManager>();

        actions.Add("bombastic", () => superMove());

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
        currentHP = healthBar.GetHealth();
        if (currentHP < prevHP)
        {
            if (currentHP <= 0)
            {
                //myRigidBody.velocity = Vector2.down * 15;

                if (!isDead)
                {
                    animator.SetBool("isDead", true);
                    isDead = true;
                }
            }
            else
            {
                animator.SetTrigger("isHurt");
                prevHP = healthBar.GetHealth();
            }
        }

        if (!isDead)
        {
            float horizontalInput = Input.GetAxis("P1-Horizontal");
            Debug.Log(horizontalInput);
            float verticalInput = Input.GetAxis("Vertical");
            float moveSpeed = 40f;

            Vector2 movement = new Vector2(horizontalInput, verticalInput) * moveSpeed;

            myRigidBody.MovePosition(myRigidBody.position + movement * Time.fixedDeltaTime);
            if (Math.Abs(horizontalInput) > 0)
            {
                StartCoroutine(runAnimation("isMoving", 1f));
            }

            /*if (Input.GetKeyDown(KeyCode.W) && lastMove != "JUMP")
            {
                Debug.Log("JUMP");
                animator.SetTrigger("isJumping");
                myRigidBody.velocity = Vector2.up * 5;
                lastMove = "JUMP";
            }*/
            
            if (move == "p1-Punch" || Input.GetKeyDown(KeyCode.P))
            {
                Debug.Log(lastMove);
                if (!combo)
                {
                    animator.ResetTrigger("isCombo");
                    lastMove = "Punch";
                    animator.SetTrigger("isPunching");
                    combo = true;
                }
                else
                {
                    animator.ResetTrigger("isPunching");
                    lastMove = "Combo";
                    animator.SetTrigger("isCombo");
                    combo = false;
                }
                
                if (myCollider.IsTouching(enemyCollider))
                {
                    Debug.Log("Hit ENEMY!");
                    //player2.TakeDamage(4);
                    if (!cooldownSM)
                    {
                        player2.TakeDamage(4);
                        mySM = sm_bar.GetSM() + 10;
                        sm_bar.SetSM(mySM);
                        count++;
                        if (count == 10)
                        {
                            sm_bar_full = true;
                            count = 0;
                        }
                    }
                    else
                    {
                        player2.TakeDamage(8);
                    }

                    sfxSounds.playSound(sfxSounds.hitEffect);
                }
            }

            if (move == "p1-Kick" || Input.GetKeyDown(KeyCode.K))
            {
                Debug.Log("KICK!");
                animator.SetTrigger("isKicking");
                if (myCollider.IsTouching(enemyCollider))
                {
                    Debug.Log("Hit ENEMY!");
                    //player2.TakeDamage(8);
                    if (!cooldownSM)
                    {
                        player2.TakeDamage(8);
                        mySM = sm_bar.GetSM() + 10;
                        sm_bar.SetSM(mySM);
                        count++;
                        if (count == 10)
                        {
                            sm_bar_full = true;
                            count = 0;
                        }
                    }
                    else
                    {
                        player2.TakeDamage(12);
                    }
                    sfxSounds.playSound(sfxSounds.hitEffect);
                }
            }
            if (move == "p1-Block" || Input.GetKey(KeyCode.B))
            {
                Debug.Log("BLOCK!");
                animator.SetTrigger("isBlocking");
                if (myCollider.IsTouching(enemyCollider))
                {
                    healthBar.SetHealth(healthBar.GetHealth());
                }
                block = true;
            }
            else
            {
                block = false;
            }
            if (Input.GetKeyDown(KeyCode.E))
            {
                currentHP--;
                healthBar.SetHealth(currentHP);
            }
            if (move == "Idle")
            {
                move = "";
            }

            if (activeSM)
            {
                StartCoroutine(SuperMoveCoroutine());       //if keyword is recognized start coroutine and set active to false
                activeSM = false;
            }
        }
    }

    public void TakeDamage(int damage)
    {
        if (block == false)
        {
            healthBar.SetHealth(healthBar.GetHealth() - damage);
        }
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.tag == "Ground")
        {
            lastMove = "";
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
        if (!cooldownSM && sm_bar_full)
        {
            activeSM = true;
            cooldownSM = true;
            sm_bar_full = false;
            //sm_bar.SetSM(0);
        }
    }

    private IEnumerator SuperMoveCoroutine()
    {
        myRigidBody.transform.localScale += new Vector3(1f, 1f, 1f);
        GetComponent<SpriteRenderer>().color = new Color(0, 1, 0, 1);

        for (int i = 100; i >= 0; i = i - 10)
        {
            sm_bar.SetSM(i);
            yield return new WaitForSeconds(1f);
        }

        //yield return new WaitForSeconds(10f);   //wait for 10 seconds

        

        myRigidBody.transform.localScale = originalScale;
        GetComponent<SpriteRenderer>().color = originalColor;

        cooldownSM = false;
    }
}
