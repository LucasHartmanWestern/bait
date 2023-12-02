// const serverPrefix = `https://visual-search-research-797f1f0ba0ac.herokuapp.com`;
const serverPrefix = 'http://127.0.0.1:8000';

export const Constants = {
  apiPaths: {
    login: `${serverPrefix}/api/v1/login`,
    register: `${serverPrefix}/api/v1/users`,
    sendMessage: `${serverPrefix}/api/v1/logConvo`,
    sendFeedback: `${serverPrefix}/api/v1/sendFeedback`,
    sendJIRA: `${serverPrefix}/api/v1/sendToJira`
  }
}
