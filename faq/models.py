from django.db import models


class FAQ(models.Model):
    """
    Model representing a Frequently Asked Question (FAQ).

    Attributes:
        question (models.CharField): The FAQ question, limited to 255 characters.
        answer (models.TextField): The detailed answer to the question.
    """
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self) -> str:
        """
        Returns the string representation of the FAQ model, which is the question text.

        Returns:
            str: The question of the FAQ.
        """
        return self.question
