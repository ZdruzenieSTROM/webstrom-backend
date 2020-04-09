from django.db import models



class Competition(models.Model):
    class Meta:
        verbose_name = 'seminár'
        verbose_name_plural = 'semináre'

    name = models.CharField(
        max_length=50,
        verbose_name='názov'
    )

    start_year = models.PositiveSmallIntegerField(
        verbose_name='rok prvého ročníka súťaže'
    )

    def __str__(self):
        return self.name


class LateTag(models.Model):
    class Meta:
        verbose_name = 'omeškanie'
        verbose_name_plural = 'omeškanie'

    name = models.CharField(
        max_length=50, verbose_name='označenie štítku pre riešiteľa')
    upper_bound = models.DurationField(
        verbose_name='maximálna dĺžka omeškania')
    comment = models.TextField(verbose_name='komentár pre opravovateľa')

    def __str__(self):
        return self.name

class Semester(models.Model):
    class Meta:
        verbose_name = 'semester'
        verbose_name_plural = 'semestre'

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE
    )

    year = models.PositiveSmallIntegerField(
        verbose_name='ročník'
    )

    start = models.DateTimeField(
        verbose_name='dátum začiatku semestra'
    )

    end = models.DateTimeField(
        verbose_name='dátum konca semestra'
    )
    late_tags = models.ManyToManyField(
        LateTag,
        verbose_name=''
    )
    season = models.CharField(
        max_length=10
        
    )

    def __str__(self):
        return f'{self.competition.name} - {self.year}. ročník {self.season} semester'

class Serie(models.Model):
    class Meta:
        verbose_name = 'séria'
        verbose_name_plural = 'série'

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name='poradie série')
    deadline = models.DateTimeField(verbose_name='termín série')
    complete = models.BooleanField(verbose_name='séria uzavretá')
    #sum_method =  # NO FOKEN IDEA

    def __str__(self):
        return f'{self.semester} - {self.order}. séria'








class Problem(models.Model):
    class Meta:
        verbose_name = 'úloha'
        verbose_name_plural = 'úlohy'

    text = models.TextField(verbose_name='znenie úlohy')
    serie = models.ForeignKey(
        Serie,
        on_delete=models.CASCADE,
        verbose_name='úloha zaradená do série'
    )
    order = models.PositiveSmallIntegerField(verbose_name='poradie v sérii')

    def __str__(self):
        return f'{self.serie.semester.competition.name}-{self.serie.semester.year}-{self.serie.semester.season}-S{self.serie.order} - {self.order}. úloha'


class Grade(models.Model):
    class Meta:
        verbose_name = 'ročník'
        verbose_name_plural = 'ročníky'

    name = models.CharField(
        max_length=32,
        verbose_name='názov ročníku'
    )
    tag = models.CharField(
        max_length=2,
        unique=True,
        verbose_name='skratka'
    )
    years_in_school = models.PositiveSmallIntegerField(
        verbose_name='počet rokov v škole'
    )
    def __str__(self):
        return self.name


class UserSemesterRegistration(models.Model):
    class Meta:
        verbose_name = 'séria'
        verbose_name_plural = 'série'

    user = models.ForeignKey('user.User', on_delete=models.CASCADE)
    school = models.ForeignKey(
        'user.School', on_delete=models.SET_NULL, null=True)
    class_level = models.ForeignKey(Grade, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

class Solution(models.Model):
    class Meta:
        verbose_name = 'riešenie'
        verbose_name_plural = 'riešenia'

    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user_semester_registration = models.ForeignKey(
        UserSemesterRegistration,
        on_delete=models.CASCADE
    )
    #solution_path =  # File field - isteho typu

    #corrected_solution_path =  # File field - isteho typu

    score = models.PositiveSmallIntegerField(verbose_name='body')

    uploaded_at = models.DateTimeField(auto_now=True, verbose_name='nahrané dňa')

    # V prípade, že riešenie prišlo po termíne nastaví sa na príslušný tag
    late_tag = models.ForeignKey(
        LateTag,
        on_delete=models.SET_NULL,
        verbose_name='',
        null=True,
        blank=True)

    is_online = models.BooleanField(
        verbose_name='internetové riešenie'
    )