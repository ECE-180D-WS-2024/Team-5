using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Windows.Speech;
using Unity.Burst.Intrinsics;
using static Unity.Collections.AllocatorManager;
using static UnityEditor.Experimental.GraphView.GraphView;

public class Player2ActionScript : MonoBehaviour
{
    public Rigidbody2D myRigidBody;
    public BoxCollider2D myCollider;
    public BoxCollider2D enemyCollider;
    public Animator animator;
    public string lastMove;
    public int maxHP = 100;
    public int prevHP;
    public int currentHP;
    public HealthBar enemyHealthBar;
    public HealthBar healthBar;
    public String move;
    public String action;
    public bool isDead;
    public bool combo;
    public int attackDamage;
    public bool block;
    public PlayerActionScript player1;
    public UDPReciever udpReciever; 

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

    // Start is called before the first frame update
    void Start()
    {
        lastMove = "";
        
        combo = false;
        block = false;
        currentHP = maxHP;
        healthBar.SetMaxHealth(maxHP);
        prevHP = healthBar.GetHealth();
        currentSM = 0;
        sm_bar.SetStartSM(0);
        sfxSounds = GameObject.FindGameObjectWithTag("Audio").GetComponent<AudioManager>();

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
        move = udpReciever.p2Move;
        action = udpReciever.p2Action;
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
            float horizontalInput = Input.GetAxis("Horizontal");
            Vector2 movement = new Vector2(0, 0);
            if (move == "p2-MoveForward")
            {
                movement = new Vector2(-6, 0);
                StartCoroutine(runAnimation("isMoving", 1f));
            }
            else if (move == "p2-MoveBackward")
            {
                movement = new Vector2(6, 0);
                StartCoroutine(runAnimation("isMoving", 1f));
            }
            else if (move == "p2-MoveStill")
            {
                movement = new Vector2(0, 0);
            }
            else if (Math.Abs(horizontalInput) > 0)
            {
                movement = new Vector2(horizontalInput, 0) * moveSpeed;
                StartCoroutine(runAnimation("isMoving", 1f));
            }

            myRigidBody.MovePosition(myRigidBody.position + movement * Time.fixedDeltaTime);

            if (Math.Abs(horizontalInput) > 0)
            {
                StartCoroutine(runAnimation("isMoving", 1f));
            }

            if (action.Contains("p2-StrongPunch") || Input.GetKeyDown(KeyCode.P) && Input.GetKeyDown(KeyCode.LeftShift))
            {
                udpReciever.p2Action = "";
                animator.SetBool("isStrongPunching", true);
                if (action.Contains("p2-StrongPunch"))
                {
                    attackDamage += int.Parse(action.Substring(14));
                }
                else
                {
                    attackDamage += 8;
                }

                if (myCollider.IsTouching(enemyCollider))
                {
                    player1.TakeDamage(attackDamage);
                    ChargeSMBar(15);

                    sfxSounds.playSound(sfxSounds.strongHitEffect);
                }
            }

            if (action == "p2-Punch" || Input.GetKeyDown(KeyCode.Space))
            {
                udpReciever.p2Action = "";
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
                    player1.TakeDamage(attackDamage);
                    ChargeSMBar(10);

                    sfxSounds.playSound(sfxSounds.hitEffect);
                }
            }
            if (action == "p2-Kick" || Input.GetKeyDown(KeyCode.M))
            {
                udpReciever.p2Action = "";
                animator.SetTrigger("isKicking");
                if (myCollider.IsTouching(enemyCollider))
                {
                    if (cooldownSM)
                    {
                        attackDamage += 4;
                    }
                    player1.TakeDamage(attackDamage);
                    ChargeSMBar(10);
                    sfxSounds.playSound(sfxSounds.hitEffect);
                }
            }
            if (action == "p2-Block" || Input.GetKey(KeyCode.L))
            {
                udpReciever.p2Action = "";
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
                StartCoroutine(SuperMoveCoroutine());
                activeSM = false;
            }
        }
        move = "";
    }

    public void TakeDamage(int damage)
    {
        damage = Mathf.Clamp(damage, 0, 15);
        Debug.Log(currentHP);
        if (block == false)
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
            sm_bar.SetSM(0);
        }
    }

    private IEnumerator SuperMoveCoroutine()
    {
        myRigidBody.transform.localScale += new Vector3(1f, 1f, 1f);
        GetComponent<SpriteRenderer>().color = new Color(1, 0, 0, 1);

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
