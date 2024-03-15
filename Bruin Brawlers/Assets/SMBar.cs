using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class SMBar : MonoBehaviour
{
    public Slider slider;
    public Image fill;

    public void SetStartSM(int status)
    {
        slider.minValue = status;
        slider.maxValue = 100;
        slider.value = status;
    }

    public void SetSM(int status)
    {
        slider.value = status;
    }

    public int GetSM()
    {
        return (int) (slider.value);
    }
}
