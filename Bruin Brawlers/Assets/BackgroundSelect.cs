using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class BackgroundSelect : MonoBehaviour
{
    public SpriteRenderer fightBackground;
    private int index = 0;
    private List<Sprite> backgrounds = new List<Sprite>();

    // Start is called before the first frame update
    void Start()
    {
        if (fightBackground == null)
        {
            Debug.LogError("No component assigned to fightBackground");
            return;
        }

        for (int i = 1; ; i++)
        {
            Sprite bg = Resources.Load<Sprite>($"background{i}");
            if (bg == null)
                break;
            backgrounds.Add(bg);
        }
        if (backgrounds.Count > 0)
        {
            fightBackground.sprite = backgrounds[index];
        }
        else
        {
            Debug.LogError("No backgrounds found in resources folder");
        }
    }

    // Update is called once per frame
    void Update()
    {
        if (Input.GetKeyDown(KeyCode.W))
        {
            index = (index + 1) % backgrounds.Count;
            fightBackground.sprite = backgrounds[index];
        }
    }
}
