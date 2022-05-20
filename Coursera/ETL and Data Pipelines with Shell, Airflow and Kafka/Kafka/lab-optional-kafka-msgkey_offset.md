<center>
    <img src="https://gitlab.com/ibm/skills-network/courses/placeholder101/-/raw/master/labs/module%201/images/IDSNlogo.png" width="300" alt="cognitiveclass.ai logo"  />
</center>

# Kafka Message key and offset

Estimated time needed: **40** minutes

## Objectives

After completing this lab, you will be able to:

*   Use message keys to keep message streams sorted in their original publication state/order

*   Use consumer offset to control and track message sequential positions in topic partitions

# Important notice about this lab environment

Please be aware that sessions for this lab environment are not persistent.
A new environment is created for you every time you connect to this lab.
Any data you may have saved in an earlier session will get lost.
To avoid losing your data, please plan to complete these labs in a single session.

# Lab environment setup and preparation

### Download and Extract Apache Kafka

Open a new terminal, by clicking on the menu bar and selecting **Terminal**->**New Terminal**, as shown in the following image.

![Screenshot highlighting New Terminal in menu](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/new-terminal.png)

This will open a new terminal at the bottom of the screen.

![Screenshot highlighting new terminal at bottom of screen](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/terminal_bottom_screen.png)

Run the following commands on the newly opened terminal. (You can copy the code by clicking on the little copy button
on the lower-right of the following codeblock and then paste it, wherever you wish.)

Download Kafka, by running the following command:

```
wget https://archive.apache.org/dist/kafka/2.8.0/kafka_2.12-2.8.0.tgz
```

{: codeblock}

Extract kafka from the zip file by running the following command:

```
tar -xzf kafka_2.12-2.8.0.tgz
```

{: codeblock}

This creates a new directory 'kafka\_2.12-2.8.0' in the current directory.

# Start ZooKeeper

ZooKeeper is required for Kafka to work. Start the ZooKeeper server.

```
cd kafka_2.12-2.8.0
bin/zookeeper-server-start.sh config/zookeeper.properties
```

{: codeblock}

When ZooKeeper starts you should see an output like this:

![Screenshot of output](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/zookeeper1.png)

You can be sure it has started when you see an output like this:

![Screenshot of output](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/zookeeper2.png)

ZooKeeper, as of this version, is required for Kafka to work.
ZooKeeper is responsible for the overall management of a Kafka cluster.
It monitors the Kafka brokers and notifies Kafka if any broker or partition goes down,
or if a new broker or partition comes up.

# Start Apache Kafka Server

Start a new terminal.

Run the following command to start Kafka server

```
cd kafka_2.12-2.8.0
bin/kafka-server-start.sh config/server.properties
```

{: codeblock}

When Kafka starts, you should see an output like this:

![](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/kafka1.png)

You can be sure it has started when you see an output like this:

![](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/kafka2.png)

# Create a topic and producer for processing bank ATM transactions

Next, we will be creating a `bankbranch` topic to process the messages that come
from the ATM machines of bank branches.

Suppose the messages come from the ATM in the form of a simple JSON object,
including an ATM id and a transaction id like the following example:

```
{"atmid": 1, "transid": 100}
```

To process the ATM messages, let's first create a new topic called `bankbranch`.

*   Start a new terminal and go to the extracted `Kafka` folder:

```
cd kafka_2.12-2.8.0
```

{: codeblock}

*   Create a new topic using the `--topic` argument with the name `bankbranch`. In order to simplify the topic configuration and better
    explain how message key and consumer offset work,  here we specify `--partitions 2` argument to create two partitions for this topic.
    You may try other `partitions` settings for this topic if you are interested in comparing the difference.

```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --create --topic bankbranch  --partitions 2
```

{: codeblock}

Now let's list all the topics to see if  `bankbranch` has been created successfully.

```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

{: codeblock}

We can also use the `--describe` command to check the details of the topic `bankbranch`

```
bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic bankbranch
```

{: codeblock}

and you can see `bankbranch` has two partitions `Partition 0` and `Partition 1`. If no message keys are specified, messages will be published to these two partitions in an alternating sequence, like this:

`Partition 0` -> `Partition 1` -> `Partition 0` -> `Partition 1` ...

Next, we can create a producer to publish some ATM transaction messages.

*   Stay in the same terminal window with the topic details, then create a producer for topic `bankbranch`

```
bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic bankbranch 

```

{: codeblock}

To produce the messages, look for the the `>` icon, and copy and paste the following ATM messages after it:

```
{"atmid": 1, "transid": 100}
```

{: codeblock}

```
{"atmid": 1, "transid": 101}
```

{: codeblock}

```
{"atmid": 2, "transid": 200}
```

{: codeblock}

```
{"atmid": 1, "transid": 102}
```

{: codeblock}

```
{"atmid": 2, "transid": 201}
```

Then, let's create a consumer in a new terminal window to consume these 5 new messages.

*   Start a new terminal and go to the extracted `Kafka` folder:

```
cd kafka_2.12-2.8.0
```

{: codeblock}

*   Then start a new consumer to subscribe to the `bankbranch` topic:

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --from-beginning
```

{: codeblock}

Then, you should see the 5 new messages we just published, but very likely, they are not consumed in the same order as they were published. Normally, you need to keep the consumed messages sorted in their original published order, especially for critical use cases such as financial transactions.

# Produce and consume with message keys

In this step, you will be using message keys to ensure that messages with the same key will be consumed in the same order as they were published. In the backend, messages with the same key will be published into the same partition and will always be consumed by the same consumer. As such, the original publication order is kept in the consumer side.

ASt this point, you should have the following four terminals open in Cloud IDE:

*   Zookeeper terminal
*   Kafka Server terminal
*   Producer terminal
*   Consumer terminal

In the next steps, you will be frequently switching among these terminals.

*   First, go to the consumer terminal and stop the consumer using `Ctrl` + `C`  (Windows)

or `Command` + `.` (Mac).

*   Then, switch to the Producer terminal and stop the previous producer.

Ok, we can now start a new producer and consumer, this time using message keys. You can start a new producer with the following message key commands:

*   `--property parse.key=true` to make the producer parse message keys
*   `--property key.separator=:` define the key separator to be the `:` character,

so our message with key now looks like the following key-value pair example:
\- `1:{"atmid": 1, "transid": 102}`.
Here the message key is `1`, which also corresponds to the ATM id, and the value is the transaction JSON object, `{"atmid": 1, "transid": 102}`.

*   Start a new producer with message key enabled:

```
bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic bankbranch --property parse.key=true --property key.separator=:
```

{: codeblock}

*   Once you see `>` symbol, you can start to produce the following messages, where you define each key to match the ATM id for each message:

```
1:{"atmid": 1, "transid": 102}
```

{: codeblock}

```
1:{"atmid": 1, "transid": 103}
```

{: codeblock}

```
2:{"atmid": 2, "transid": 202}
```

{: codeblock}

```
2:{"atmid": 2, "transid": 203}
```

{: codeblock}

```
1:{"atmid": 1, "transid": 104}
```

{: codeblock}

*   Next, switch to the consumer terminal again, and start a new consumer with

`--property print.key=true --property key.separator=:` arguments to print the keys

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --from-beginning --property print.key=true --property key.separator=:
```

{: codeblock}

Now, you should see that messages that have the same key are being consumed in the same order (e.g., `trans102 -> trans103 -> trans104`) as they were published.

This is because each topic partition maintains its own message queue, and new messages are enqueued (appended to the end of the queue)
as they get published to the partition. Once consumed, the earliest messages will be dequeued and nno longer be available for consumption.

Recall that with two partitions and no message keys specified, the transaction messages were published to the two partitions
in rotation:

*   Partition 0: `[{"atmid": 1, "transid": 102}, {"atmid": 2, "transid": 202}, {"atmid": 1, "transid": 104}]`
*   Partition 1: `[{"atmid": 1, "transid": 103}, {"atmid": 2, "transid": 203}]`

As you can see, the transaction messages from `atm1` and `atm2` got scattered across both partitions. It would be difficult
to unravel this and consume messages from one ATM with the same order as they were published.

However, with message key specified as the `atmid` value, the messages from the two ATMs will look like the following:

*   Partition 0: `[{"atmid": 1, "transid": 102}, {"atmid": 1, "transid": 103}, {"atmid": 1, "transid": 104}]`
*   Partition 1: `[{"atmid": 2, "transid": 202}, {"atmid": 2, "transid": 203}]`

Messages with the same key will always be published to the same partition, so that their published order will be preserved within the message queue of each partition.

As such, we can keep the states or orders of the transactions for each ATM.

# Consumer Offset

Topic partitions keeps published messages in a sequence, like a list.
Message offset indicates a message's position in the sequence. For example,
the offset of an empty Partition 0 of `bankbranch` is `0`, and if you publish the first message
to the partition, its offset will be `1`.

By using offsets in the consumer, you can specify the starting position for message consumption, such as from the beginning to retrieve all messages, or from some later point to retrieve only the latest messages.

## Consumer Group

In addition, we normally group related consumers together as a consumer group.
For example, we may want to create a consumer for each ATM in the bank and manage all ATM related consumers
together in a group.

So let's see how to create a consumer group, which is actually very easy with the `--group` argument.

*   In the consumer terminal, stop the previous consumer if it is still running.

*   Run the following command to create a new consumer within a consumer group called `atm-app`:

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```

{: codeblock}

After the consumer within the `atm-app` consumer group is started, you should not expect any messages to be consumed.
This is because the offsets for both partitions have already reached to the end.
In other words, all messages have already been consumed, and therefore dequeued, by previous consumers.

You can verify that by checking consumer group details.

*   Stop the consumer.

*   Show the details of the consumer group `atm-app`:

```
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group atm-app
```

{: codeblock}

Now you should see the offset information for the topic `bankbranch`:
![](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/consumer_details_lag0.png)

Recall that we have published `10` messages in total, and we can see the `CURRENT-OFFSET` column of partition 1 is `6`
and `CURRENT-OFFSET` of partition 0 is `4`, and they add up to 10 messages.

The `LOG-END-OFFSET`column indicates the last offset or the end of the sequence, which is 6 for partition 1 and 4 for
partition 0. Thus, both partitions have reached the end of their queues and no more messages are available for consumption.

Meanwhile, you can check the `LAG` column which represents the count of unconsumed messages for each partition.
Currently it is `0` for all partitions, as expected.

Now, let's produce more messages and see how the offsets change.

*   Switch to the previous producer terminal, and publish two more messages:

```
1:{"atmid": 1, "transid": 105}
```

{: codeblock}

```
2:{"atmid": 2, "transid": 204}
```

{: codeblock}

and let's switch back to the consumer terminal and check the consumer group details again:

```
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group atm-app
```

{: codeblock}

![](https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DB0250EN-SkillsNetwork/labs/Streaming/images/consumer_details_lag1.png)

You should see that both offsets have been increased by 1, and the `LAG` columns for both partitions have become
`1`. It means we have 1 new message for each partition to be consumed.

*   Let's start the consumer again and see whether the two new messages will be consumed.

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```

{: codeblock}

OK, now both partitions have reached the end once again. But what if you want to consume the messages again from the beginning?

We can do that via resetting offset in the next step.

## Reset offset

We can reset the index with the `--reset-offsets` argument.

First let's try resetting the offset to the earliest position (beginning) using `--reset-offsets --to-earliest`.

*   Stop the previous consumer if it is still running, and run the following command to reset the offset:

```
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092  --topic bankbranch --group atm-app --reset-offsets --to-earliest --execute
```

{: codeblock}

Now the offsets have been set to 0 (the beginning).

*   Start the consumer again:

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```

{: codeblock}

You should see that all 12 messages are consumed and that all offsets have reached the partition ends again.

In fact, you can reset the offset to any position. For example, let's reset the offset so that
we only consume the last two messages.

*   Stop the previous consumer

*   Shift the offset to left by 2 using `--reset-offsets --shift-by -2`:

```
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092  --topic bankbranch --group atm-app --reset-offsets --shift-by -2 --execute
```

{: codeblock}

*   If you run the consumer again, you should see that we consumed 4 messages, 2 for each partition:

```
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic bankbranch --group atm-app
```

{: codeblock}

# Summary

In this lab, you have learned how to include message keys in publication to keep their message states/order.
You have also learned how to reset the offset to control the message consumption starting point.

## Authors

[Yan Luo](https://www.linkedin.com/in/yan-luo-96288783/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkCoursesIBMDB0250ENSkillsNetwork26764073-2021-01-01)

### Other Contributors

## Change Log

| Date (YYYY-MM-DD) | Version | Changed By | Change Description                 |
| ----------------- | ------- | ---------- | ---------------------------------- |
| 2021-10-27        | 1.0     | Yan Luo    | Created initial version of the lab |

Copyright (c) 2021 IBM Corporation. All rights reserved.
