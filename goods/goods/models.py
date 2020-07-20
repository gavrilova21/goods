from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Advertisement(models.Model):
    title = models.CharField(verbose_name="Название", max_length=120)
    price = models.PositiveIntegerField(verbose_name="Цена")
    date = models.DateTimeField(verbose_name="Дата размещения", auto_now_add=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    image = models.FileField(
        verbose_name="Изображение", upload_to="images/", null=True, blank=True
    )
    views = models.PositiveIntegerField(default=0, editable=False)

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views += 1
        super().save()
