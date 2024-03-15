using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Xml.Serialization;
using UnityEngine;
using UnityEngine.Windows.Speech;

public class Player2ActionScript : MonoBehaviour
{
    public Rigidbody2D myRigidBody;
    public BoxCollider2D myCollider;
    public BoxCollider2D enemyCollider;
    public Animator animator;
    public string lastMove;
    public int maxHP = 100;
    public int currentHP;
    public HealthBar enemyHealthBar;
    public HealthBar healthBar;

    public int maxSM = 100;
    public int currentSM;
    public SMBar sm_bar;
    public int count = 0;

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
        lastMove = "";
        currentHP = maxHP;
        healthBar.SetMaxHealth(maxHP);
        currentSM = 0;
        sm_bar.SetStartSM(0);

        actions.Add("fergalicious", () => superMove());

        keywordRecognizer = new KeywordRecognizer(actions.Keys.ToArray());
        keywordRecognizer.OnPhraseRecognized += RecognizedSpeech;
        keywordRecognizer.Start();

        originalScale = myRigidBody.transform.localScale;
        originalColor = GetComponent<SpriteRenderer>().color;
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
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Debug.Log("PUNCH!");
            animator.SetTrigger("isPunching");
            if (myCollider.IsTouching(enemyCollider))
            {
                Debug.Log("Hit ENEMY!");
                int enemyHP = enemyHealthBar.GetHealth() - 4;
                enemyHealthBar.SetHealth(enemyHP);
                if (!cooldownSM)
                {
                    int mySM = sm_bar.GetSM() + 10;
                    sm_bar.SetSM(mySM);
                    count++;
                    if (count == 10)
                    {
                        sm_bar_full = true;
                        count = 0;
                    }
                }
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
        if (!cooldownSM && sm_bar_full)
        {
            activeSM = true;
            cooldownSM = true;
            sm_bar_full = false;
            sm_bar.SetSM(0);
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
