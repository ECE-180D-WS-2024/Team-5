using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerActionScript : MonoBehaviour
{
    public Rigidbody2D myRigidBody;
    public Animator animator;
    public float time;
    public float lastSwitch;
    public string lastMove;

    // Start is called before the first frame update
    void Start()
    {
        time = 0;
        lastSwitch = 0;
        lastMove = "";
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.W) && lastMove != "JUMP")
        {
            Debug.Log("JUMP");
            animator.SetTrigger("isJumping");
            myRigidBody.velocity = Vector2.up * 5;
            lastMove = "JUMP";
        }
        if (Input.GetKeyDown(KeyCode.A))
        {
            //animator.SetBool("isMoving", true);
            myRigidBody.velocity = Vector2.left * 15;
            animator.SetBool("isMoving", true);
        }
        if (Input.GetKeyDown(KeyCode.S))
        {
            myRigidBody.velocity = Vector2.down * 15;
            //animator.SetBool("isMoving", true);
        }
        if (Input.GetKeyDown(KeyCode.D))
        {
            //animator.SetBool("isMoving", true);
            myRigidBody.velocity = Vector2.right * 15;
            //animator.SetBool("isMoving", true);
            StartCoroutine(runAnimation("isMoving", 2f));
        }
        if (Input.GetKeyDown(KeyCode.P))
        {
            Debug.Log("PUNCH!");
            animator.SetTrigger("isPunching");
        }
        if (Input.GetKeyDown(KeyCode.K))
        {
            Debug.Log("KICK!");
        }
        if (Input.GetKeyDown(KeyCode.L))
        {
            Debug.Log("BLOCK!");
        }
    }

    private void OnCollisionEnter2D(Collision2D collision)
    {
        lastMove = "";
        Debug.Log("RESET LAST MOVE");
        //Debug.Log(collision);
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
}
