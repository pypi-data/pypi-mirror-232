const ACKNOWLEDGMENT_TYPES = {
  DISMISSED: "dismissed",
  CONFIRMED: "confirmed"
}

function confirmNoticeClick(forwarding_url_override){
  const url = forwarding_url_override || forwardingUrl;
  sendAcknowledgment(ACKNOWLEDGMENT_TYPES.CONFIRMED, url)
}

function dismissNoticeClick(event){
  let nextUrl;
  if (event.currentTarget.href){
    // If caller is a link, stop redirection until after API call.
    event.preventDefault();
    nextUrl = event.currentTarget.href;
  } else {
    nextUrl = forwardingUrl;
  }
  sendAcknowledgment(ACKNOWLEDGMENT_TYPES.DISMISSED, nextUrl)
};

function sendAcknowledgment(type, url){
  const callback = () => {
    window.location = url;
  }
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  let params = { notice_id: noticeId, acknowledgment_type: type};
  let postRequest = new XMLHttpRequest();
  postRequest.open("POST", "/notices/api/v1/acknowledge");
  postRequest.setRequestHeader("Content-type", "application/json");
  postRequest.setRequestHeader("X-CSRFToken", csrftoken);
  postRequest.send(JSON.stringify(params));
  postRequest.onreadystatechange = () => {
    if (postRequest.readyState === 4 && postRequest.status === 204) {
      console.log("acknowledgment successful");
      window.analytics.track('edx.bi.user.acknowledged_notice', {...params});
      callback();
    } else if (postRequest.readyState === 4 && postRequest.status !== 204) {
      /* We need to let the user exit even on a failure because mobile users can get stuck otherwise */
      console.log(`acknowledgement failed. Error: ${postRequest.responseText}`)
      callback();
    }
  };
}
