using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AudioManager : MonoBehaviour
{
    [SerializeField] AudioSource musicSource;
    [SerializeField] AudioSource SFXSource;

    public AudioClip background;
    public AudioClip hitEffect;

    private void Start()
    {
        musicSource.clip = background;
        musicSource.Play();
    }

    public void playSound(AudioClip clip)
    {
        SFXSource.PlayOneShot(clip);
    }
}
