def sendEmail(int wait_time, int failed){
    println (wait_time * failed)
}

return [
    sendEmail: this.&sendEmail
]