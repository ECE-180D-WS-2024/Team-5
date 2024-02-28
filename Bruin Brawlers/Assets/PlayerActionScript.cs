using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerActionScript : MonoBehaviour
{
    public Rigidbody2D myRigidBody;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.W) == true)
        {
            myRigidBody.velocity = Vector2.up * 5;
        }
        else if(Input.GetKeyDown(KeyCode.A) == true)
        {
            myRigidBody.velocity = Vector2.left * 15;
        }
        else if (Input.GetKeyDown(KeyCode.S) == true)
        {
            myRigidBody.velocity = Vector2.down * 5;
        }
        else if (Input.GetKeyDown(KeyCode.D) == true)
        {
            myRigidBody.velocity = Vector2.right * 15;
        }
    }
}
