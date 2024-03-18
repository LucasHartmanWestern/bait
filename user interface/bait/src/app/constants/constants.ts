//const serverPrefix = `https://bait-app-df10e84632ed.herokuapp.com`; // Heroku
//const serverPrefix = 'http://127.0.0.1:8000'; // Localhost
const serverPrefix = 'http://34.130.172.219:8000'; // GCP

export const Constants = {
  apiPaths: {
    login: `${serverPrefix}/api/v1/login`,
    register: `${serverPrefix}/api/v1/users`,
    sendMessage: `${serverPrefix}/api/v1/logConvo`,
    sendFeedback: `${serverPrefix}/api/v1/sendFeedback`,
    sendJIRA: `${serverPrefix}/api/v1/sendToJira`
  }
}
