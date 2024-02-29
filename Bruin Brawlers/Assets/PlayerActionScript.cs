using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerActionScript : MonoBehaviour
{
    public Rigidbody2D myRigidBody;
    public Sprite idle;
    public Sprite punch;
    public float time;
    public float lastSwitch;

    // Start is called before the first frame update
    void Start()
    {
        time = 0;
        lastSwitch = 0;
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.W))
        {
            myRigidBody.velocity = Vector2.up * 5;
        }
        if (Input.GetKeyDown(KeyCode.A))
        {
            myRigidBody.velocity = Vector2.left * 15;
        }
        if (Input.GetKeyDown(KeyCode.S))
        {
            myRigidBody.velocity = Vector2.down * 5;
        }
        if (Input.GetKeyDown(KeyCode.D))
        {
            myRigidBody.velocity = Vector2.right * 15;
        }
        if (Input.GetKeyDown(KeyCode.P))
        {
            Debug.Log("PUNCH!");
            GetComponent<SpriteRenderer>().sprite = punch;
            lastSwitch = 40 * Time.deltaTime;
            time = 0;
        }
        if (Input.GetKeyDown(KeyCode.K))
        {
            Debug.Log("KICK!");
        }
        if (Input.GetKeyDown(KeyCode.L))
        {
            Debug.Log("BLOCK!");
        }

        time += Time.deltaTime;
        Debug.Log(time);
        Debug.Log(lastSwitch);
        if (time >= lastSwitch)
        {
            GetComponent<SpriteRenderer>().sprite = idle;
            Debug.Log("return to idle");
        }
    }

    private void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.gameObject.CompareTag("Player"))
        {
            Debug.Log("Collision with Enemy");
            Rigidbody enemyRigidbody = collision.gameObject.GetComponent<Rigidbody>();
            enemyRigidbody.velocity = Vector2.right * 15;
        }
        else
        {
            Debug.Log(collision.gameObject.tag);
        }
    }
}
