using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Windows.Speech;
using UnityEngine.SceneManagement;
using TMPro;

public class PlayerActionScript : MonoBehaviour
{
    public Rigidbody2D myRigidBody;
    public BoxCollider2D myCollider;
    public BoxCollider2D enemyCollider;
    public Animator animator;
    public int maxHP = 100;
    public int currentHP;
    public int prevHP;
    public string lastMove;
    public HealthBar healthBar;
    public String move;
    public String action;
    public int attackDamage;
    public bool isDead;
    public bool combo;
    public bool block;
    public Player2ActionScript player2;
    
    public AudioManager sfxSounds;
    public int maxSM = 100;
    public int currentSM;
    public SMBar sm_bar;
    public int count = 0;
    public int mySM = 0;

    private KeywordRecognizer keywordRecognizer;
    private Dictionary<string, Action> actions = new Dictionary<string, Action>();
    private Vector3 originalScale;
    private Color originalColor;
    private bool activeSM = false;
    private bool cooldownSM = false;
    private bool sm_bar_full = false;

    public GameOverScreen gameOverScreen;
    private Scene scene;
    public TextMeshProUGUI outOfBoundsText;

    // Start is called before the first frame update
    void Start()
    {
        scene = SceneManager.GetActiveScene();
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
        actions.Add("pause", () => gameOverScreen.Pause());

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
        string move = UDPReciever.p1Move;
        string action = UDPReciever.p1Action;

        animator.SetBool("isStrongPunching", false);
        attackDamage = 2;

        currentHP = healthBar.GetHealth();
        if (currentHP < prevHP)
        {
            if (currentHP <= 0)
            {
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
            float moveSpeed = 30f;
            float horizontalInput = Input.GetAxis("P1-Horizontal");
            Vector2 movement = new Vector2(0, 0);
            if (move == "p1-MoveForward")
            {
                movement = new Vector2(10, 0);
                StartCoroutine(runAnimation("isMoving", 1f));
            }
            else if (move == "p1-MoveBackward")
            {
                movement = new Vector2(-10, 0);
                StartCoroutine(runAnimation("isMoving", 1f));
            }
            else if (move == "p1-MoveStill")
            {
                movement = new Vector2(0, 0);                
            }
            else if (Math.Abs(horizontalInput) > 0)
            {
                movement = new Vector2(horizontalInput, 0) * moveSpeed;
                StartCoroutine(runAnimation("isMoving", 1f));
            }

            myRigidBody.MovePosition(myRigidBody.position + movement * Time.fixedDeltaTime);


            if (action.Contains("p1-StrongPunch") || Input.GetKeyDown(KeyCode.O))
            {
                UDPReciever.p1Action = "";
                animator.SetBool("isStrongPunching", true);
                if (action.Contains("p1-StrongPunch"))
                {
                    attackDamage += int.Parse(action.Substring(14));
                }
                else
                {
                    attackDamage += 8;
                }

                if (myCollider.IsTouching(enemyCollider))
                {
                    player2.TakeDamage(attackDamage);
                    ChargeSMBar(15);

                    sfxSounds.playSound(sfxSounds.strongHitEffect);
                }
            }
            if (action == "p1-Punch" || Input.GetKeyDown(KeyCode.P))
            {
                UDPReciever.p1Action = "";
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
                    if (cooldownSM)
                    {
                        attackDamage += 4;
                    }
                    player2.TakeDamage(attackDamage);
                    ChargeSMBar(10);

                    sfxSounds.playSound(sfxSounds.hitEffect);
                }
            }

            if (action == "p1-Kick" || Input.GetKeyDown(KeyCode.K))
            {
                UDPReciever.p1Action = "";
                animator.SetTrigger("isKicking");
                if (myCollider.IsTouching(enemyCollider))
                {
                    if (cooldownSM)
                    {
                        attackDamage += 4;
                    }
                    player2.TakeDamage(attackDamage);
                    ChargeSMBar(10);
                    sfxSounds.playSound(sfxSounds.hitEffect);
                }
            }
            if (action == "p1-Block" || Input.GetKey(KeyCode.B))
            {
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
            if (activeSM)
            {
                StartCoroutine(SuperMoveCoroutine());       //if keyword is recognized start coroutine and set active to false
                activeSM = false;
            }

            if (move == "p1-MoveError")
            {
                if (outOfBoundsText.text == "p2-MoveError")
                {
                    outOfBoundsText.text = "P1 and P2 out of bounds!";
                }
                else
                {
                    outOfBoundsText.text = "P1 out of bounds!";
                }
            }
            else
            {
                outOfBoundsText.text = "";
            }
        }
        move = "";
    }

    public void TakeDamage(int damage)
    {
        damage = Mathf.Clamp(damage, 0, 15);
        if (block == false && scene.name == "Game")
        {
            currentHP -= damage;
            healthBar.SetHealth(currentHP);
        }
        else
        {
            currentHP -= damage / 8;
            healthBar.SetHealth(currentHP);
        }
    }

    private void ChargeSMBar(int amount)
    {
        if (!cooldownSM)
        {
            mySM = sm_bar.GetSM() + amount;
            sm_bar.SetSM(mySM);
            count++;
            if (count == 10)
            {
                sm_bar_full = true;
                count = 0;
            }
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

    private void OnDestroy()
    {
        keywordRecognizer.Stop();
    }
}
