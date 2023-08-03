import wave
import struct

# No additional imports allowed!


def backwards(sound):
    samplesList = sound["samples"].copy()
    samplesList.reverse()
    rateInt = sound["rate"]
    reversedSound = {"rate": rateInt, "samples": samplesList}
    return reversedSound


def mix(sound1, sound2, p):

    # mix 2 good sounds
    if (
        "rate" in sound1.keys()
        and "rate" in sound2.keys()
        and sound1["rate"] == sound2["rate"]
    ) == False:

        print("no")
        return

    try:
        r = sound1["rate"]  # get rate
        sound1 = sound1["samples"]
        sound2 = sound2["samples"]
        if len(sound1) < len(sound2):
            l = len(sound1)
        elif len(sound2) < len(sound1):
            l = len(sound2)
        elif len(sound1) == len(sound2):
            l = len(sound1)
        else:
            print("whoops")
            return

        s = []
        x = 0
        while x <= l:
            s2, s1 = p * sound1[x], sound2[x] * (1 - p)
            s.append(s1 + s2)  # add sounds
            x += 1
            if x == l:  # end
                break

        return {"rate": r, "samples": s}  # return new sound

    except KeyError:
        rate = sound1["rate"]  # get rate
        sound_left_1 = sound1["left"]
        sound_right_1 = sound1["right"]
        sound_left_2 = sound2["left"]
        sound_right_2 = sound2["right"]

        if len(sound_left_1) > len(sound_left_2):
            length = len(sound_left_2)
        else:
            length = len(sound_left_1)

        i = 0
        s_left = []
        s_right = []

        while i <= length - 1:
            s_left2, s_left1 = p * sound_left_1[i], (1 - p) * sound_left_2[i]
            s_right2, s_right1 = p * sound_right_1[i], (1 - p) * sound_right_2[i]
            s_left.append(s_left1 + s_left2)  # add sounds
            s_right.append(s_right1 + s_right2)
            i += 1

        return {"rate": rate, "left": s_left, "right": s_right}  # return new sound


def convolve(sound, kernel):
    """
    Applies a filter to a sound, resulting in a new sound that is longer than
    the original mono sound by the length of the kernel - 1.
    Does not modify inputs.

    Args:
        sound: A mono sound dictionary with two key/value pairs:
            * "rate": an int representing the sampling rate, samples per second
            * "samples": a list of floats containing the sampled values
        kernel: A list of numbers

    Returns:
        A new mono sound dictionary.
    """
    samples = sound["samples"]

    final_sample = [0] * (len(samples) + len(kernel) - 1)

    for i, number in enumerate(kernel):
        if number != 0:
            for x, sample in enumerate(samples):
                final_sample[i + x] += sample * number

    return {"rate": sound["rate"], "samples": final_sample}


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
        scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """

    rate = sound["rate"]

    delay_n = round(delay * rate)
    total_length = num_echoes * delay_n
    echo_filter = [1]

    for x in range(num_echoes):
        if x == 0:
            echo_filter += [0] * (total_length)
        offset = delay_n * (x + 1)
        print(offset, len(echo_filter))
        echo_filter[offset] = scale ** (x + 1)

    return convolve(sound, echo_filter)


def pan(sound):
    left_channel = sound["left"].copy()
    scaled_left_sample = []

    right_channel = sound["right"].copy()
    scaled_right_sample = []

    for i, sample in enumerate(left_channel):
        if i == 0:
            scaled_left_sample.append(sample * 1)
            scaled_right_sample.append(right_channel[i] * 0)
        elif i == len(left_channel):
            scaled_left_sample.append(sample * 0)
            scaled_left_sample.append(right_channel[i] * 1)
        else:
            scaled_left_sample.append(sample * (1 - (i / (len(left_channel) - 1))))
            scaled_right_sample.append(right_channel[i] * (i / (len(left_channel) - 1)))

    return {
        "rate": sound["rate"],
        "left": scaled_left_sample,
        "right": scaled_right_sample,
    }


def remove_vocals(sound):
    left_sample = sound["left"].copy()
    right_sample = sound["right"].copy()
    difference_sample = []

    for i, sample in enumerate(left_sample):
        difference_sample.append(sample - right_sample[i])

    return {"rate": sound["rate"], "samples": difference_sample}


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def bass_boost_kernel(boost, scale=0):
    """
    Constructs a kernel that acts as a bass-boost filter.

    We start by making a low-pass filter, whose frequency response is given by
    (1/2 + 1/2cos(Omega)) ^ N

    Then we scale that piece up and add a copy of the original signal back in.

    Args:
        boost: an int that controls the frequencies that are boosted (0 will
            boost all frequencies roughly equally, and larger values allow more
            focus on the lowest frequencies in the input sound).
        scale: a float, default value of 0 means no boosting at all, and larger
            values boost the low-frequency content more);

    Returns:
        A list of floats representing a bass boost kernel.
    """
    # make this a fake "sound" so that we can use the convolve function
    base = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    kernel = {"rate": 0, "samples": [0.25, 0.5, 0.25]}
    for i in range(boost):
        kernel = convolve(kernel, base["samples"])
    kernel = kernel["samples"]

    # at this point, the kernel will be acting as a low-pass filter, so we
    # scale up the values by the given scale, and add in a value in the middle
    # to get a (delayed) copy of the original
    kernel = [i * scale for i in kernel]
    kernel[len(kernel) // 2] += 1

    return kernel


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)

    # hello = load_wav("sounds/hello.wav")
    # write_wav(backwards(hello), "hello_reversed.wav")

    # mystery = load_wav("sounds/mystery.wav")
    # write_wav(backwards(mystery), "mystery_reversed.wav")

    # synth = load_wav("sounds/synth.wav")
    # water = load_wav("sounds/water.wav")
    # write_wav(mix(synth, water, 0.2), "mixed.wav")

    # ice_and_chilli = load_wav("sounds/ice_and_chilli.wav")
    # write_wav(convolve(ice_and_chilli, bass_boost_kernel(1000, 1.5)), "base_boost_ice_and_chilli.wav")

    # car = load_wav("sounds/car.wav", stereo=True)
    # write_wav(pan(car), "left_to_right_car.wav")

    # lookout_mountain = load_wav("sounds/lookout_mountain.wav", stereo=True)
    # write_wav(remove_vocals(lookout_mountain), "mono_lookout_mountain.wav")

    #chord = load_wav("sounds/chord.wav")
    #write_wav(echo(chord, 5, .3, .6), "echo_chord.wav")

    # synth = load_wav("sounds/synth.wav", stereo = True)
    # water = load_wav("sounds/water.wav", stereo = True)
    # write_wav(mix(synth, water, 0.3), "remixed.wav")

    pass