# For formatting use HTML

def getInterviewMail(slotTime):
    interview = f""" Hello,<br>
<i>Thanks for your interest in KOSS</i>. Your scheduled interview slot is on <b>{slotTime}</b>.<br>
Meet link: <b><a href="https://meet.google.com/ycq-ywhn-ajm">https://meet.google.com/ycq-ywhn-ajm</a></b> (<i>Join this lobby in the above-mentioned slot and</i> <b>mention your name in the chat box</b>. <i>You will be called for a personal interview once a panel becomes free.</i>)<br><br>

<i>Kindly join during the slot mentioned above or reply to this mail in case of any issues with the timings. Due to a lot of applications and busy slots, rescheduling the meeting can be difficult for us, so we request you to stick with your slots and ask for a reschedule only if absolutely necessary.</i><br><br>
"""
    return interview

def getTaskMail(name, taskURL, deadline):
    task = f"""Hello {name},<br><br>
Congratulations! You have made it to the second round of selections. You can find your task in the GitHub link below.<br><br>

<a href="{taskURL}">{taskURL}</a><br><br>

<i>The task may seem daunting at first because it is daunting given the time frame. However, we are more concerned with your approach rather than the final delivery</i>.<br><br>

We expect you to upload your code/presentation to a GitHub repository and share the link with us as a reply to this email by <b>{deadline}, at 1 AM</b>.<br><br>

Round - 2 Interview is scheduled for <b>{deadline}</b> tentatively. The exact timings will be mailed later.<br><br>

In case of any issues with the task, or if you want to change your task, please drop us a mail or contact any of us.<br><br>

Happy Learning!<br><br>
"""
    return task

rejection = f"""Hello,<br><br>
            
We are afraid to be writing with some bad news. Unfortunately, we would not be able to extend your selection application to Kharagpur Open Source Society.<br><br>

The selections this year have by far been the toughest we have experienced, even after stretching the interview and judging process for many days.<br><br>

Your caliber was outstanding to the point that we found ourselves, unfortunately, having to turn down even the most highly qualified applicants with fantastic submissions. We tried our best to increase the amount of intake this year, but we don't have the bandwidth to be able to take on more of you and still ensure you all have a great experience.<br><br>

Even if you’re not a part of KOSS, we still hope to work together to spread Open Source awareness in Kharagpur because it takes a whole village to do that. We’re rooting for you and looking forward to seeing what you do next.<br><br>

Here are some resources below which you may find useful:
    
    <ol>
    <li><a href="https://rejected.us/">We've All Faced Rejection</a></li>
    <li><a href="https://github.com/deepanshu1422/List-Of-Open-Source-Internships-Programs">List of Open Source Internship Programs</a></li>
    <li><a href="https://slack.metakgp.org/">Invitation to MetaKGP Slack</a></li>
    <li><a href="https://1x.engineer/">1x Engineer</a></li>
    <li><a href="https://github.com/codecrafters-io/build-your-own-x">Build Your Own X</a></li>
    </ol>
"""

def getOnboardingMail(name, number_of_applicants):
    onboarding = f"""Hi {name},<br><br>

<b>Congratulations and Welcome to KOSS!</b><br><br>

We're sure that you've been waiting for the results of the selections. We really appreciate you giving time to our interview sessions and completing the given task on time, especially with endsems approaching.<br><br>

We had a great time with you in our selection process. We received over <b>{number_of_applicants} applications</b> and the selections this year have by far been the toughest we have experienced, even after stretching the interview and judging process for many days.<br><br>

Your answers and experience caught our attention. In the interview, we found that your vision was similar to ours and thus you will be a perfect addition to our team. We know we will enjoy working with you and we'll have to work hard to keep up with your enthusiasm!<br><br>

We cannot express how thrilled we are through this email! We would love to meet you as soon as we can. <i>You will receive an email soon with the details of induction sessions which will introduce you to everybody at KOSS.</i><br><br>

<i>As a part of your onboarding process, we'll add you to the KOSS Slack workspace which we use for discussion and planning.</i> <b>In case you want to use a different email to join the workspace, do let us know and we'll send an invite there instead.</b> Also, check out different channels and explore around to make sure you're comfortable with using Slack.<br><br>

Cheers!<br><br>
    """
    return onboarding

signature = f"""--<br>
Regards,<br>
Kharagpur Open Source Society<br>
IIT Kharagpur<br>
<a href="https://kossiitkgp.org/">Website</a> | <a href="https://github.com/kossiitkgp">GitHub</a> | <a href="https://facebook.com/kossiitkgp">Facebook</a> | <a href="https://twitter.com/kossiitkgp">Twitter</a>
"""
