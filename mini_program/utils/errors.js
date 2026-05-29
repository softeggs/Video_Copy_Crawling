function normalizeErrorMessage(error, fallbackMessage) {
  if (!error) {
    return fallbackMessage;
  }

  if (typeof error === "string") {
    return error;
  }

  if (error.message) {
    return error.message;
  }

  return fallbackMessage;
}

module.exports = {
  normalizeErrorMessage
};
